from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class CrappyProviderError(RuntimeError):
    def __init__(self, message: str, retry_after_seconds: int | None = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


@dataclass(frozen=True)
class CrappyMessage:
    role: str
    content: str


@dataclass(frozen=True)
class CrappyProviderRequest:
    messages: tuple[CrappyMessage, ...]

    @classmethod
    def from_messages(cls, messages: Iterable[CrappyMessage]) -> "CrappyProviderRequest":
        return cls(tuple(messages))


@dataclass(frozen=True)
class CrappyProviderResponse:
    text: str
    provider: str
    model: str
    request_id: str | None = None


class CrappyProvider:
    name = "base"

    def generate(self, request: CrappyProviderRequest) -> CrappyProviderResponse:
        raise NotImplementedError
