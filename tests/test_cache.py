import csv

from pashtobench.cache import CachingClient, cache_key, prompt_hash
from pashtobench.clients import ModelResponse


class CountingClient:
    """A stand in model client that counts how often it is really called."""

    spec = None

    def __init__(self):
        self.calls = 0

    def complete(self, prompt, system=None):
        self.calls += 1
        return ModelResponse(
            text="reply",
            model="fake",
            input_tokens=7,
            output_tokens=3,
            cost_usd=0.0001,
        )


def test_prompt_hash_changes_with_system():
    assert prompt_hash("p") != prompt_hash("p", system="s")


def test_cache_key_shape():
    key = cache_key("pbt-tr-001", "hello")
    assert key.startswith("pbt-tr-001__")


def test_miss_then_hit(tmp_path):
    inner = CountingClient()
    caching = CachingClient(
        inner,
        "fake",
        cache_dir=tmp_path / "raw",
        cost_log=tmp_path / "cost_log.csv",
    )

    first = caching.complete("pbt-tr-001", "translate this")
    assert first.cached is False
    assert inner.calls == 1

    second = caching.complete("pbt-tr-001", "translate this")
    assert second.cached is True
    assert inner.calls == 1  # served from cache, no new provider call
    assert second.text == "reply"


def test_cost_log_written_once(tmp_path):
    inner = CountingClient()
    log = tmp_path / "cost_log.csv"
    caching = CachingClient(inner, "fake", cache_dir=tmp_path / "raw", cost_log=log)

    caching.complete("pbt-tr-001", "a")
    caching.complete("pbt-tr-001", "a")  # cached, must not log again

    rows = list(csv.reader(log.open(encoding="utf-8")))
    assert rows[0] == ["model", "item_id", "input_tokens", "output_tokens", "cost_usd"]
    assert len(rows) == 2  # header plus one logged call
    assert rows[1][0] == "fake"
    assert rows[1][2] == "7"
