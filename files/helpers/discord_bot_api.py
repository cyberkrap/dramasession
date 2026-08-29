import json
import os
import threading
import time

import requests


_API_URL = os.getenv("OBSESSION_BOT_API_URL", "").strip().rstrip("/")
_MAX_RESPONSE_BYTES = 1024 * 1024
_CATALOG_TTL_SECONDS = 60
_HEALTH_TTL_SECONDS = 10
_CACHE_LOCK = threading.Lock()
_CACHE = {
    "catalog": (0.0, None),
    "health": (0.0, None),
}


def bot_api_configured():
    return bool(_API_URL)


def _declared_content_length(response):
    value = response.headers.get("Content-Length")
    if not value:
        return None

    try:
        length = int(value)
    except (TypeError, ValueError):
        return None

    return length if length >= 0 else None


def _fetch_json(path):
    if not _API_URL:
        return None

    response = requests.get(
        f"{_API_URL}{path}",
        headers={"User-Agent": "TheObsessionClub/discordbot-hub"},
        timeout=(2.0, 4.0),
        stream=True,
    )
    response.raise_for_status()

    content_length = _declared_content_length(response)
    if content_length is not None and content_length > _MAX_RESPONSE_BYTES:
        raise ValueError("Obsession Bot API response exceeded size limit")

    chunks = []
    total = 0
    for chunk in response.iter_content(chunk_size=16384):
        if not chunk:
            continue
        total += len(chunk)
        if total > _MAX_RESPONSE_BYTES:
            raise ValueError("Obsession Bot API response exceeded size limit")
        chunks.append(chunk)

    return json.loads(b"".join(chunks).decode("utf-8"))


def _cached_fetch(key, path, ttl):
    now = time.monotonic()
    with _CACHE_LOCK:
        expires_at, cached = _CACHE[key]
        if cached is not None and expires_at > now:
            return cached

    value = _fetch_json(path)
    with _CACHE_LOCK:
        _CACHE[key] = (now + ttl, value)
    return value


def _clean_string(value, max_length=500):
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]


def get_command_catalog():
    try:
        raw = _cached_fetch("catalog", "/v1/commands", _CATALOG_TTL_SECONDS)
    except (requests.RequestException, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(raw, dict) or raw.get("version") != 1:
        return None

    raw_commands = raw.get("commands")
    if not isinstance(raw_commands, list):
        return None

    commands = []
    for item in raw_commands[:500]:
        if not isinstance(item, dict):
            continue

        name = _clean_string(item.get("name"), 80)
        kind = _clean_string(item.get("kind"), 20)
        category = _clean_string(item.get("category"), 80)
        description = _clean_string(item.get("description"), 500)
        if not name or kind not in {"prefix", "slash"} or not category:
            continue

        aliases = item.get("aliases") if isinstance(item.get("aliases"), list) else []
        examples = item.get("examples") if isinstance(item.get("examples"), list) else []
        permissions = item.get("permissions") if isinstance(item.get("permissions"), list) else []

        commands.append({
            "name": name,
            "kind": kind,
            "category": category,
            "description": description,
            "usage": _clean_string(item.get("usage"), 200),
            "aliases": [_clean_string(value, 80) for value in aliases[:20] if _clean_string(value, 80)],
            "examples": [_clean_string(value, 200) for value in examples[:20] if _clean_string(value, 200)],
            "permissions": [_clean_string(value, 100) for value in permissions[:20] if _clean_string(value, 100)],
        })

    categories = sorted({command["category"] for command in commands}, key=str.casefold)
    return {
        "generated_at": _clean_string(raw.get("generatedAt"), 80),
        "default_prefix": _clean_string(raw.get("defaultPrefix"), 20) or ",",
        "categories": categories,
        "commands": commands,
    }


def get_bot_health():
    try:
        raw = _cached_fetch("health", "/healthz", _HEALTH_TTL_SECONDS)
    except (requests.RequestException, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(raw, dict):
        return None

    return {
        "ready": raw.get("ready") is True,
        "guild_count": raw.get("guildCount") if isinstance(raw.get("guildCount"), int) else None,
        "ping_ms": raw.get("websocketPingMs") if isinstance(raw.get("websocketPingMs"), int) else None,
        "uptime_seconds": raw.get("uptimeSeconds") if isinstance(raw.get("uptimeSeconds"), int) else None,
    }
