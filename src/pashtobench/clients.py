"""Model client layer: one interface over several providers.

I talk to each provider over HTTP with httpx so the whole benchmark uses a
single uniform interface. Caching and cost logging wrap these clients in
cache.py. Prices and model ids live in the registry below; check them against
current provider pricing before a real run.
"""

import os
from dataclasses import dataclass
from typing import Protocol

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


@dataclass
class ModelResponse:
    """One model reply plus the usage and cost I record for it."""

    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    cached: bool = False


@dataclass(frozen=True)
class Price:
    """US dollars per million tokens, input and output."""

    input_per_m: float
    output_per_m: float

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * self.input_per_m + output_tokens * self.output_per_m) / 1_000_000


@dataclass(frozen=True)
class ModelSpec:
    name: str  # short benchmark name, e.g. claude
    provider: str  # openai, anthropic or gemini
    model_id: str  # the provider's own model id
    price: Price
    env_key: str  # env var holding the api key
    base_url: str = ""  # for the openai compatible providers


# The six benchmark arms. Model ids and prices marked "verify" are placeholders
# to confirm before a paid run. The Claude price is current as of July 2026.
REGISTRY: dict[str, ModelSpec] = {
    "gpt": ModelSpec(
        "gpt",
        "openai",
        "gpt-4o",
        Price(2.5, 10.0),  # verify id and price
        env_key="OPENAI_API_KEY",
        base_url="https://api.openai.com/v1",
    ),
    "claude": ModelSpec(
        "claude",
        "anthropic",
        "claude-sonnet-5",
        Price(3.0, 15.0),
        env_key="ANTHROPIC_API_KEY",
    ),
    "gemini": ModelSpec(
        "gemini",
        "gemini",
        "gemini-2.5-pro",
        Price(1.25, 5.0),  # verify
        env_key="GOOGLE_API_KEY",
    ),
    "llama": ModelSpec(
        "llama",
        "openai",
        "meta-llama/llama-3.3-70b-instruct",
        Price(0.6, 0.6),  # verify
        env_key="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
    ),
    "qwen": ModelSpec(
        "qwen",
        "openai",
        "qwen/qwen-2.5-72b-instruct",
        Price(0.4, 0.4),  # verify
        env_key="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
    ),
    "aya": ModelSpec(
        "aya",
        "openai",
        "cohere/aya-expanse-32b",
        Price(0.5, 1.5),  # verify
        env_key="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
    ),
}


def list_specs() -> list[ModelSpec]:
    return list(REGISTRY.values())


class ModelClient(Protocol):
    spec: ModelSpec

    def complete(self, prompt: str, system: str | None = None) -> ModelResponse: ...


class RetryableError(Exception):
    """A transient failure I retry: a network drop, a 429 or a 5xx."""


class _BaseClient:
    def __init__(
        self,
        spec: ModelSpec,
        http: httpx.Client | None = None,
        api_key: str | None = None,
    ) -> None:
        self.spec = spec
        self.http = http or httpx.Client(timeout=60.0)
        self.api_key = api_key if api_key is not None else os.environ.get(spec.env_key, "")

    @retry(
        reraise=True,
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, max=30),
        retry=retry_if_exception_type(RetryableError),
    )
    def _post_json(
        self,
        url: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:
        try:
            response = self.http.post(url, headers=headers, params=params, json=json)
        except httpx.TransportError as exc:
            raise RetryableError(str(exc)) from exc
        if response.status_code == 429 or response.status_code >= 500:
            raise RetryableError(f"http {response.status_code}")
        response.raise_for_status()
        return response.json()


class OpenAICompatibleClient(_BaseClient):
    """OpenAI, OpenRouter, Groq and anything speaking the chat completions API."""

    def complete(self, prompt: str, system: str | None = None) -> ModelResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        data = self._post_json(
            f"{self.spec.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.spec.model_id,
                "messages": messages,
                "temperature": 0,
                "max_tokens": 1024,
            },
        )
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return self._response(
            text, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
        )

    def _response(self, text: str, input_tokens: int, output_tokens: int) -> ModelResponse:
        return ModelResponse(
            text=text,
            model=self.spec.model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=self.spec.price.cost(input_tokens, output_tokens),
        )


class AnthropicClient(_BaseClient):
    ENDPOINT = "https://api.anthropic.com/v1/messages"
    VERSION = "2023-06-01"

    def complete(self, prompt: str, system: str | None = None) -> ModelResponse:
        body: dict = {
            "model": self.spec.model_id,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system
        # I do not send temperature: the current Claude models reject it.
        data = self._post_json(
            self.ENDPOINT,
            headers={"x-api-key": self.api_key, "anthropic-version": self.VERSION},
            json=body,
        )
        text = "".join(
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        )
        usage = data.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        return ModelResponse(
            text=text,
            model=self.spec.model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=self.spec.price.cost(input_tokens, output_tokens),
        )


class GeminiClient(_BaseClient):
    BASE = "https://generativelanguage.googleapis.com/v1beta/models"

    def complete(self, prompt: str, system: str | None = None) -> ModelResponse:
        body: dict = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 1024},
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        data = self._post_json(
            f"{self.BASE}/{self.spec.model_id}:generateContent",
            params={"key": self.api_key},
            json=body,
        )
        candidate = data["candidates"][0]
        text = "".join(part.get("text", "") for part in candidate["content"]["parts"])
        usage = data.get("usageMetadata", {})
        input_tokens = usage.get("promptTokenCount", 0)
        output_tokens = usage.get("candidatesTokenCount", 0)
        return ModelResponse(
            text=text,
            model=self.spec.model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=self.spec.price.cost(input_tokens, output_tokens),
        )


_CLIENTS = {
    "openai": OpenAICompatibleClient,
    "anthropic": AnthropicClient,
    "gemini": GeminiClient,
}


def build_client(spec: ModelSpec, http: httpx.Client | None = None) -> ModelClient:
    return _CLIENTS[spec.provider](spec, http=http)


def client_for(name: str, http: httpx.Client | None = None) -> ModelClient:
    return build_client(REGISTRY[name], http=http)
