from __future__ import annotations

import base64
import json
import os
import re
import threading
import time

import requests

from .provider import (
    CrappyProvider,
    CrappyProviderError,
    CrappyProviderRequest,
    CrappyProviderResponse,
    CrappyToolExecutor,
)


GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1/interactions"
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
DEFAULT_GEMINI_RPM = 10.0

_rate_lock = threading.Lock()
_next_request_at = 0.0
_provider_cooldown_until = 0.0


def _configured_rpm() -> float:
    raw = (os.environ.get("CRAPPY_GEMINI_RPM") or str(DEFAULT_GEMINI_RPM)).strip().lower()
    if raw in {"0", "off", "false", "disabled"}:
        return 0.0
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return DEFAULT_GEMINI_RPM
    return max(1.0, min(value, 120.0))


def _wait_for_request_slot() -> None:
    """Pace all Gemini calls in this worker, including tool-call followups."""
    global _next_request_at

    rpm = _configured_rpm()
    if rpm <= 0:
        return

    interval = 60.0 / rpm
    while True:
        with _rate_lock:
            now = time.monotonic()
            ready_at = max(_next_request_at, _provider_cooldown_until)
            wait_for = ready_at - now
            if wait_for <= 0:
                _next_request_at = now + interval
                return
        time.sleep(min(wait_for, 1.0))


def _set_provider_cooldown(seconds: int | float | None) -> None:
    global _provider_cooldown_until

    try:
        delay = float(seconds or 0)
    except (TypeError, ValueError):
        delay = 0.0
    if delay <= 0:
        return

    with _rate_lock:
        _provider_cooldown_until = max(
            _provider_cooldown_until,
            time.monotonic() + min(delay, 86400.0),
        )


class GeminiCrappyProvider(CrappyProvider):
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = (api_key or os.environ.get("GEMINI_API_KEY") or "").strip()
        self.model = (
            model
            or os.environ.get("CRAPPY_MODEL")
            or os.environ.get("CRAPPY_GEMINI_MODEL")
            or DEFAULT_GEMINI_MODEL
        ).strip()
        if not self.api_key:
            raise CrappyProviderError("GEMINI_API_KEY is not configured")
        if not self.model:
            raise CrappyProviderError("No Gemini model is configured")

    @staticmethod
    def _compile_request(request: CrappyProviderRequest) -> tuple[str, str]:
        system_blocks = []
        input_blocks = []
        for message in request.messages:
            role = (message.role or "user").strip().lower()
            content = (message.content or "").strip()
            if not content:
                continue
            if role == "system":
                system_blocks.append(content)
            else:
                input_blocks.append(f"[{role.upper()}]\n{content}")
        if not input_blocks:
            raise CrappyProviderError("Crappy provider request has no user content")
        return "\n\n".join(system_blocks), "\n\n".join(input_blocks)

    @staticmethod
    def _input_content(request: CrappyProviderRequest, input_text: str) -> list[dict]:
        content: list[dict] = [{"type": "text", "text": input_text}]
        for media in request.media:
            if media.kind != "image" or not media.data or not media.mime_type.startswith("image/"):
                continue
            if media.source:
                content.append(
                    {
                        "type": "text",
                        "text": f"Attached TOC image from {media.source}:",
                    }
                )
            content.append(
                {
                    "type": "image",
                    "mime_type": media.mime_type,
                    "data": base64.b64encode(media.data).decode("ascii"),
                }
            )
        return content

    @staticmethod
    def _tool_payload(request: CrappyProviderRequest) -> list[dict]:
        return [
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in request.tools
        ]

    @staticmethod
    def _extract_text(data: dict) -> str:
        if isinstance(data.get("output_text"), str) and data["output_text"].strip():
            return data["output_text"].strip()

        chunks = []
        for step in data.get("steps") or []:
            if not isinstance(step, dict) or step.get("type") != "model_output":
                continue
            for item in step.get("content") or []:
                if isinstance(item, dict) and item.get("type") == "text" and item.get("text"):
                    chunks.append(str(item["text"]))

        if not chunks:
            for output in data.get("outputs") or []:
                if isinstance(output, dict) and output.get("type") == "text" and output.get("text"):
                    chunks.append(str(output["text"]))

        return "\n".join(chunks).strip()

    @staticmethod
    def _function_calls(data: dict) -> list[dict]:
        calls = []
        for step in data.get("steps") or []:
            if isinstance(step, dict) and step.get("type") == "function_call":
                calls.append(step)
        return calls

    @staticmethod
    def _duration_seconds(value) -> int | None:
        text = str(value or "").strip().lower()
        match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)s", text)
        if not match:
            return None
        try:
            return max(1, int(float(match.group(1)) + 0.999))
        except (TypeError, ValueError):
            return None

    @classmethod
    def _retry_after(cls, response, error_payload: dict | None = None) -> int | None:
        value = response.headers.get("Retry-After")
        if value:
            try:
                return max(1, int(float(value)))
            except (TypeError, ValueError):
                pass

        error = error_payload.get("error", {}) if isinstance(error_payload, dict) else {}
        for item in error.get("details") or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("@type") or "").endswith("google.rpc.RetryInfo"):
                parsed = cls._duration_seconds(item.get("retryDelay"))
                if parsed is not None:
                    return parsed

        if response.status_code == 429:
            return 60
        if response.status_code >= 500:
            return 15
        return None

    def _post_interaction(self, payload: dict) -> dict:
        _wait_for_request_slot()

        try:
            response = requests.post(
                GEMINI_INTERACTIONS_URL,
                headers={
                    "x-goog-api-key": self.api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=(5, 45),
            )
        except requests.RequestException as exc:
            raise CrappyProviderError(
                f"Gemini request failed: {exc}", retry_after_seconds=15
            ) from exc

        if response.status_code != 200:
            detail = response.text[:500]
            error_payload = None
            try:
                error_payload = response.json()
                detail = str(error_payload.get("error", {}).get("message") or detail)[:500]
            except (ValueError, AttributeError):
                pass

            retry_after = self._retry_after(response, error_payload)
            if response.status_code == 429:
                # A 429 applies to the Gemini project, not just one queue row.
                # Cool down the whole worker so the next queued mention does not
                # immediately hammer the same exhausted quota window.
                _set_provider_cooldown(retry_after or 60)

            raise CrappyProviderError(
                f"Gemini returned HTTP {response.status_code}: {detail}",
                retry_after_seconds=retry_after,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise CrappyProviderError(
                "Gemini returned invalid JSON", retry_after_seconds=15
            ) from exc

    def generate(
        self,
        request: CrappyProviderRequest,
        tool_executor: CrappyToolExecutor | None = None,
    ) -> CrappyProviderResponse:
        system_instruction, input_text = self._compile_request(request)
        tools = self._tool_payload(request)

        # Keep tool calling stateless. Gemini requires every model-generated step
        # (including thought/function_call steps) to be replayed exactly on each
        # subsequent request when store=false.
        history: list[dict] = [
            {
                "type": "user_input",
                "content": self._input_content(request, input_text),
            }
        ]
        last_data: dict = {}

        for round_index in range(request.max_tool_rounds + 1):
            payload = {
                "model": self.model,
                "input": history,
                "store": False,
            }
            if system_instruction:
                payload["system_instruction"] = system_instruction
            if tools:
                payload["tools"] = tools

            data = self._post_interaction(payload)
            last_data = data
            steps = [step for step in (data.get("steps") or []) if isinstance(step, dict)]
            history.extend(steps)

            calls = self._function_calls(data)
            if not calls:
                text = self._extract_text(data)
                if not text:
                    raise CrappyProviderError("Gemini returned no text output")
                return CrappyProviderResponse(
                    text=text,
                    provider=self.name,
                    model=str(data.get("model") or self.model),
                    request_id=str(data.get("id") or "") or None,
                )

            if tool_executor is None or not tools:
                raise CrappyProviderError(
                    "Gemini requested a tool but no Crappy tool executor is available"
                )
            if round_index >= request.max_tool_rounds:
                raise CrappyProviderError("Crappy exceeded the maximum tool-call rounds")

            for call in calls:
                name = str(call.get("name") or "").strip()
                call_id = str(call.get("id") or "").strip()
                arguments = call.get("arguments")
                if not isinstance(arguments, dict):
                    arguments = {}

                try:
                    result = tool_executor(name, arguments)
                    result_payload = {"ok": True, "data": result}
                except Exception as exc:
                    # Tool failures are model-visible data, not provider/network
                    # failures. This lets Crappy explain that a lookup is unavailable
                    # instead of retrying the whole queue job.
                    result_payload = {
                        "ok": False,
                        "error": f"{type(exc).__name__}: {exc}"[:1000],
                    }

                history.append(
                    {
                        "type": "function_result",
                        "name": name,
                        "call_id": call_id,
                        "result": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    result_payload,
                                    ensure_ascii=False,
                                    separators=(",", ":"),
                                ),
                            }
                        ],
                    }
                )

        raise CrappyProviderError(
            f"Gemini tool loop ended without text output ({last_data.get('id') or 'unknown interaction'})"
        )
