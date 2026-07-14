"""Response cache and cost log that wrap any model client.

Every call is cached to results/raw/ keyed by model, item id and a hash of the
prompt, so a rerun never pays the provider twice. Each uncached call appends a
row to the cost log. The raw cache is the audit trail for every published score.
"""

import csv
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from pashtobench.clients import ModelClient, ModelResponse


def prompt_hash(prompt: str, system: str | None = None) -> str:
    digest = hashlib.sha256()
    digest.update((system or "").encode("utf-8"))
    digest.update(b"\x00")
    digest.update(prompt.encode("utf-8"))
    return digest.hexdigest()[:16]


def cache_key(item_id: str, prompt: str, system: str | None = None) -> str:
    return f"{item_id}__{prompt_hash(prompt, system)}"


class CachingClient:
    """Wraps a model client with an on disk cache and a cost log."""

    def __init__(
        self,
        client: ModelClient,
        model_name: str,
        cache_dir: str | Path = "results/raw",
        cost_log: str | Path = "results/cost_log.csv",
    ) -> None:
        self.client = client
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) / model_name
        self.cost_log = Path(cost_log)

    def complete(self, item_id: str, prompt: str, system: str | None = None) -> ModelResponse:
        path = self.cache_dir / f"{cache_key(item_id, prompt, system)}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            response = ModelResponse(**data)
            response.cached = True
            return response

        response = self.client.complete(prompt, system=system)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(response), ensure_ascii=False), encoding="utf-8")
        self._log_cost(item_id, response)
        return response

    def _log_cost(self, item_id: str, response: ModelResponse) -> None:
        self.cost_log.parent.mkdir(parents=True, exist_ok=True)
        first_time = not self.cost_log.exists()
        with self.cost_log.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            if first_time:
                writer.writerow(["model", "item_id", "input_tokens", "output_tokens", "cost_usd"])
            writer.writerow(
                [
                    self.model_name,
                    item_id,
                    response.input_tokens,
                    response.output_tokens,
                    f"{response.cost_usd:.6f}",
                ]
            )
