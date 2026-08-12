from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from files.classes import Marsey
from files.helpers.config.const import EMOJI_SRCS

from .provider import CrappyToolDefinition


_APP_ROOT = Path(__file__).resolve().parents[3]
_STATIC_EMOTE_DIR = Path(__file__).resolve().parents[2] / "assets" / "images" / "emojis"
_APPROVED_EMOTE_DIR = Path("/asset_submissions/marseys/approved")
_EMOTE_TOKEN_RE = re.compile(r":([a-z0-9_!#@-]{1,36}):", re.IGNORECASE)
_WORD_RE = re.compile(r"[a-z0-9_+-]+", re.IGNORECASE)
_GENERIC_EMOJI_RE = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001FAFF"
    "\u2300-\u23FF"
    "\u2600-\u27BF"
    "]",
    re.UNICODE,
)
_SEARCH_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "for", "from", "in", "is",
    "it", "of", "on", "or", "that", "the", "this", "to", "with",
}
_SEARCH_EMOTES_TOOL = "search_toc_emotes"
_MAX_SEARCH_RESULTS = 12


def _json_source_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return _APP_ROOT / path


def _tag_values(value) -> list[str]:
    if isinstance(value, str):
        values = value.split()
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        values = []

    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        tag = str(item or "").strip().lower()
        if tag and tag not in seen:
            seen.add(tag)
            result.append(tag)
    return result


def _active_emote_catalog(db) -> dict[str, dict[str, Any]]:
    """Build the actual renderable TOC emote catalog with live DB tags."""
    static_names = {
        path.stem.lower()
        for path in _STATIC_EMOTE_DIR.glob("*.webp")
        if path.is_file()
    }

    catalog: dict[str, dict[str, Any]] = {}
    for source in EMOJI_SRCS:
        path = _json_source_path(str(source))
        try:
            raw_items = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(raw_items, list):
            continue

        for raw in raw_items:
            if not isinstance(raw, dict):
                continue
            name = str(raw.get("name") or "").strip().lower()
            if not name or name not in static_names:
                continue
            catalog[name] = {
                "name": name,
                "tags": set(_tag_values(raw.get("tags"))) | {name},
                "count": int(raw.get("count") or 0),
                "category": str(raw.get("class") or "").strip(),
            }

    # File presence is the final source of truth for bundled emotes, even when a
    # legacy JSON entry does not carry useful metadata.
    for name in static_names:
        catalog.setdefault(
            name,
            {
                "name": name,
                "tags": {name},
                "count": 0,
                "category": "",
            },
        )

    rows = (
        db.query(Marsey)
        .filter(Marsey.submitter_id == None)
        .order_by(Marsey.name.asc())
        .all()
    )
    for marsey in rows:
        name = str(marsey.name or "").strip().lower()
        if not name:
            continue
        if name not in static_names and not (_APPROVED_EMOTE_DIR / f"{name}.webp").is_file():
            # Do not teach Crappy zombie DB entries whose image file is gone.
            continue

        entry = catalog.setdefault(
            name,
            {
                "name": name,
                "tags": {name},
                "count": 0,
                "category": "",
            },
        )
        entry["tags"].update(_tag_values(marsey.tags))
        entry["tags"].add(name)
        entry["count"] = int(marsey.count or entry.get("count") or 0)

    return catalog


def _query_terms(query: str) -> list[str]:
    result = []
    for term in _WORD_RE.findall(str(query or "").lower()):
        if len(term) <= 1 or term in _SEARCH_STOP_WORDS or term in result:
            continue
        result.append(term)
    return result[:16]


def search_toc_emotes(db, query: str, limit: int = 8) -> dict[str, Any]:
    catalog = _active_emote_catalog(db)
    terms = _query_terms(query)
    phrase = " ".join(terms)

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 8
    limit = max(1, min(limit, _MAX_SEARCH_RESULTS))

    scored = []
    for entry in catalog.values():
        name = entry["name"]
        tags = set(entry["tags"])
        searchable = " ".join([name, *sorted(tags)])
        score = 0
        matched = 0

        if phrase and name == phrase.replace(" ", ""):
            score += 1000
        if phrase and phrase in searchable:
            score += 120

        for term in terms:
            term_score = 0
            if term == name:
                term_score = max(term_score, 300)
            elif name.startswith(term):
                term_score = max(term_score, 150)
            elif term in name:
                term_score = max(term_score, 100)

            if term in tags:
                term_score = max(term_score, 220)
            elif any(tag.startswith(term) for tag in tags):
                term_score = max(term_score, 120)
            elif any(term in tag for tag in tags):
                term_score = max(term_score, 70)

            if term_score:
                matched += 1
                score += term_score

        if terms and matched == len(terms):
            score += 100
        if not terms:
            score = 1
        if score <= 0:
            continue

        scored.append(
            (
                score,
                int(entry.get("count") or 0),
                name,
                {
                    "name": name,
                    "token": f":{name}:",
                    "tags": sorted(tags)[:24],
                    "usage_count": int(entry.get("count") or 0),
                    "category": entry.get("category") or None,
                },
            )
        )

    scored.sort(key=lambda item: (-item[0], -item[1], item[2]))
    return {
        "query": str(query or "").strip(),
        "results": [item[3] for item in scored[:limit]],
        "returned": min(len(scored), limit),
    }


def normalize_crappy_output(db, text: str) -> str:
    """Ban generic Unicode emoji while preserving text emoticons and valid TOC emotes."""
    output = str(text or "")
    output = _GENERIC_EMOJI_RE.sub("", output)
    output = output.replace("\uFE0F", "").replace("\u200D", "").replace("\u20E3", "")

    active_names = set(_active_emote_catalog(db))

    def validate_token(match: re.Match) -> str:
        raw = match.group(1).lower()
        name = raw.replace("!", "").replace("#", "")
        if name in active_names or name == "marseyrandom":
            return match.group(0)
        if name.endswith("pat") and name[:-3] in active_names:
            return match.group(0)
        return ""

    output = _EMOTE_TOKEN_RE.sub(validate_token, output)
    output = re.sub(r"[ \t]{2,}", " ", output)
    output = re.sub(r"[ \t]+\n", "\n", output)
    return output.strip()


@dataclass
class CrappyToolSuite:
    db: Any
    base: Any

    @property
    def definitions(self):
        return tuple(self.base.definitions) + (
            CrappyToolDefinition(
                name=_SEARCH_EMOTES_TOOL,
                description=(
                    "Search the live TOC emote catalog by emote name and search tags. "
                    "Use mood/action concepts such as greeting, wave, excited, laugh, sad, "
                    "celebrate, shocked, or whatever tone fits the reply. Results contain "
                    "verified :name: tokens that are safe to use in a TOC comment. Do not "
                    "invent an emote token that this tool did not return."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "A short semantic search made of mood/action/reaction keywords."
                            ),
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": _MAX_SEARCH_RESULTS,
                            "description": "Maximum candidate emotes to return.",
                        },
                    },
                    "required": ["query"],
                },
            ),
        )

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        if str(name or "") == _SEARCH_EMOTES_TOOL:
            return search_toc_emotes(
                self.db,
                str((arguments or {}).get("query") or ""),
                (arguments or {}).get("limit", 8),
            )
        return self.base.execute(name, arguments or {})
