import pytest

from pashtobench.clients import (
    REGISTRY,
    AnthropicClient,
    GeminiClient,
    ModelResponse,
    ModelSpec,
    OpenAICompatibleClient,
    Price,
    build_client,
    client_for,
)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise AssertionError(f"status {self.status_code}")

    def json(self):
        return self._payload


class FakeHttp:
    """Records the last request and returns a canned payload."""

    def __init__(self, payload):
        self.payload = payload
        self.last = None

    def post(self, url, headers=None, params=None, json=None):
        self.last = {"url": url, "headers": headers, "params": params, "json": json}
        return FakeResponse(self.payload)


def test_price_cost():
    price = Price(3.0, 15.0)
    # 1000 input + 500 output at 3/15 per million
    assert price.cost(1000, 500) == pytest.approx((1000 * 3 + 500 * 15) / 1_000_000)


def test_response_defaults():
    r = ModelResponse(text="hi", model="m")
    assert r.cost_usd == 0.0
    assert r.cached is False


def test_registry_has_six_arms():
    assert set(REGISTRY) == {"gpt", "claude", "gemini", "llama", "qwen", "aya"}
    assert REGISTRY["claude"].provider == "anthropic"
    assert REGISTRY["claude"].price == Price(3.0, 15.0)


def test_build_client_picks_class():
    assert isinstance(client_for("claude"), AnthropicClient)
    assert isinstance(client_for("gpt"), OpenAICompatibleClient)
    assert isinstance(client_for("gemini"), GeminiClient)


def test_openai_client_parses_and_costs():
    spec = ModelSpec("x", "openai", "m", Price(1.0, 2.0), env_key="X", base_url="http://api")
    http = FakeHttp(
        {
            "choices": [{"message": {"content": "salaam"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }
    )
    client = build_client(spec, http=http)
    client.api_key = "k"
    resp = client.complete("hello", system="be brief")
    assert resp.text == "salaam"
    assert resp.input_tokens == 10
    assert resp.output_tokens == 5
    assert resp.cost_usd == pytest.approx((10 * 1.0 + 5 * 2.0) / 1_000_000)
    # system prompt is sent as the first message
    assert http.last["json"]["messages"][0]["role"] == "system"
    assert http.last["json"]["temperature"] == 0


def test_anthropic_client_omits_temperature():
    spec = ModelSpec("c", "anthropic", "claude-x", Price(3.0, 15.0), env_key="A")
    http = FakeHttp(
        {
            "content": [{"type": "text", "text": "ورور"}],
            "usage": {"input_tokens": 8, "output_tokens": 4},
        }
    )
    client = build_client(spec, http=http)
    resp = client.complete("translate")
    assert resp.text == "ورور"
    assert resp.output_tokens == 4
    assert "temperature" not in http.last["json"]


def test_gemini_client_parses():
    spec = ModelSpec("g", "gemini", "gemini-x", Price(1.0, 1.0), env_key="G")
    http = FakeHttp(
        {
            "candidates": [{"content": {"parts": [{"text": "answer"}]}}],
            "usageMetadata": {"promptTokenCount": 3, "candidatesTokenCount": 2},
        }
    )
    client = build_client(spec, http=http)
    resp = client.complete("q")
    assert resp.text == "answer"
    assert resp.input_tokens == 3
