"""Turn cached run outputs into per model scores on disk.

I join the runner's outputs with the data references, score each model with the
translation scorer per direction, and write results/scores/{task}.json for the
leaderboard to render. Errored calls and items without a reference are skipped.
"""

import json
from dataclasses import asdict
from pathlib import Path

from pashtobench.runner import load_task_items
from pashtobench.scorers.translation import score_by_direction


def _read_outputs(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def score_translation_run(
    data_dir: str | Path = "data",
    results_dir: str | Path = "results",
) -> dict:
    results_dir = Path(results_dir)
    items = {item.id: item for item in load_task_items("translation", data_dir)}
    outputs = _read_outputs(results_dir / "outputs" / "translation.jsonl")

    by_model: dict[str, list[dict]] = {}
    for record in outputs:
        by_model.setdefault(record["model"], []).append(record)

    scores: list[dict] = []
    for model, records in by_model.items():
        triples = []
        for record in records:
            if record.get("error"):
                continue
            item = items.get(record["item_id"])
            if item is None or not item.reference:
                continue
            triples.append((record["output"], item.reference, item.direction))
        for corpus in score_by_direction(triples).values():
            entry = asdict(corpus)
            entry["model"] = model
            scores.append(entry)

    payload = {"task": "translation", "scores": scores}
    dest = results_dir / "scores" / "translation.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload
