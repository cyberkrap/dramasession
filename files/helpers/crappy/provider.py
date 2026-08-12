from __future__ import annotations

import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import unquote, urlparse


_CRAPPY_IMAGE_ROOT = Path("/images")
_CRAPPY_IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+['\"][^)]*['\"])?\s*\)",
    re.IGNORECASE,
)
_CRAPPY_MAX_IMAGES = 3
_CRAPPY_MAX_IMAGE_BYTES = 6 * 1024 * 1024
_CRAPPY_MAX_TOTAL_MEDIA_BYTES = 12 * 1024 * 1024


class CrappyProviderError(RuntimeError):
    def __init__(self, message: str, retry_after_seconds: int | None = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


@dataclass(frozen=True)
class CrappyMessage:
    role: str
    content: str


@dataclass(frozen=True)
class CrappyMedia:
    kind: str
    mime_type: str
    data: bytes
    source: str | None = None


@dataclass(frozen=True)
class CrappyToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


CrappyToolExecutor = Callable[[str, dict[str, Any]], Any]


def _local_image_media(messages: Iterable[CrappyMessage]) -> tuple[CrappyMedia, ...]:
    """Load TOC-owned /images attachments referenced by request context.

    Only local uploaded images are eligible. Remote URLs are deliberately ignored,
    so provider context construction cannot become an SSRF surface.
    """
    try:
        image_root = _CRAPPY_IMAGE_ROOT.resolve()
    except OSError:
        image_root = _CRAPPY_IMAGE_ROOT

    found: list[CrappyMedia] = []
    seen: set[str] = set()
    total_bytes = 0

    for message in messages:
        for match in _CRAPPY_IMAGE_RE.finditer(message.content or ""):
            raw_url = str(match.group(1) or "").strip()
            parsed = urlparse(raw_url)
            if parsed.scheme or parsed.netloc:
                continue

            url_path = unquote(parsed.path or "")
            if not url_path.startswith("/images/"):
                continue
            relative = url_path[len("/images/"):]
            if not relative or relative in seen:
                continue

            candidate = (image_root / relative).resolve()
            try:
                candidate.relative_to(image_root)
            except ValueError:
                continue
            if not candidate.is_file():
                continue

            try:
                size = candidate.stat().st_size
            except OSError:
                continue
            if size <= 0 or size > _CRAPPY_MAX_IMAGE_BYTES:
                continue
            if total_bytes + size > _CRAPPY_MAX_TOTAL_MEDIA_BYTES:
                continue

            mime_type = mimetypes.guess_type(candidate.name)[0] or "image/webp"
            if not mime_type.startswith("image/"):
                continue

            try:
                data = candidate.read_bytes()
            except OSError:
                continue
            if len(data) != size:
                continue

            seen.add(relative)
            total_bytes += size
            found.append(
                CrappyMedia(
                    kind="image",
                    mime_type=mime_type,
                    data=data,
                    source=url_path,
                )
            )
            if len(found) >= _CRAPPY_MAX_IMAGES:
                return tuple(found)

    return tuple(found)


@dataclass(frozen=True)
class CrappyProviderRequest:
    messages: tuple[CrappyMessage, ...]
    media: tuple[CrappyMedia, ...] = ()
    tools: tuple[CrappyToolDefinition, ...] = ()
    max_tool_rounds: int = 4

    @classmethod
    def from_messages(
        cls,
        messages: Iterable[CrappyMessage],
        tools: Iterable[CrappyToolDefinition] = (),
        max_tool_rounds: int = 4,
        media: Iterable[CrappyMedia] = (),
    ) -> "CrappyProviderRequest":
        message_items = tuple(messages)
        explicit_media = tuple(media)
        discovered_media = _local_image_media(message_items)
        return cls(
            message_items,
            explicit_media + discovered_media,
            tuple(tools),
            max(0, int(max_tool_rounds)),
        )


@dataclass(frozen=True)
class CrappyProviderResponse:
    text: str
    provider: str
    model: str
    request_id: str | None = None


class CrappyProvider:
    name = "base"

    def generate(
        self,
        request: CrappyProviderRequest,
        tool_executor: CrappyToolExecutor | None = None,
    ) -> CrappyProviderResponse:
        raise NotImplementedError
