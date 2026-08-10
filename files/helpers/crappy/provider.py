from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable


class CrappyProviderError(RuntimeError):
    def __init__(self, message: str, retry_after_seconds: int | None = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


@dataclass(frozen=True)
class CrappyMessage:
    role: str
    content: str


@dataclass(frozen=True)
class CrappyToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


CrappyToolExecutor = Callable[[str, dict[str, Any]], Any]


@dataclass(frozen=True)
class CrappyProviderRequest:
    messages: tuple[CrappyMessage, ...]
    tools: tuple[CrappyToolDefinition, ...] = ()
    max_tool_rounds: int = 4

    @classmethod
    def from_messages(
        cls,
        messages: Iterable[CrappyMessage],
        tools: Iterable[CrappyToolDefinition] = (),
        max_tool_rounds: int = 4,
    ) -> "CrappyProviderRequest":
        return cls(tuple(messages), tuple(tools), max(0, int(max_tool_rounds)))


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
