from __future__ import annotations

import os

import requests

from .provider import (
    CrappyProvider,
    CrappyProviderError,
    CrappyProviderRequest,
    CrappyProviderResponse,
)


GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1/interactions"
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"


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

    def generate(self, request: CrappyProviderRequest) -> CrappyProviderResponse:
        system_instruction, input_text = self._compile_request(request)
        payload = {
            "model": self.model,
            "input": input_text,
            "store": False,
        }
        if system_instruction:
            payload["system_instruction"] = system_instruction

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
            raise CrappyProviderError(f"Gemini request failed: {exc}") from exc

        if response.status_code != 200:
            detail = response.text[:500]
            try:
                payload = response.json()
                detail = str(payload.get("error", {}).get("message") or detail)[:500]
            except (ValueError, AttributeError):
                pass
            raise CrappyProviderError(f"Gemini returned HTTP {response.status_code}: {detail}")

        try:
            data = response.json()
        except ValueError as exc:
            raise CrappyProviderError("Gemini returned invalid JSON") from exc

        text = self._extract_text(data)
        if not text:
            raise CrappyProviderError("Gemini returned no text output")

        return CrappyProviderResponse(
            text=text,
            provider=self.name,
            model=str(data.get("model") or self.model),
            request_id=str(data.get("id") or "") or None,
        )
