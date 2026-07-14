"""The evaluation runner: task by model, cached and resumable.

For each model and each item I build the prompt, call the caching client, and
record the reply. Because every call goes through the cache, a rerun skips work
already done, so a run is resumable and never pays the provider twice. One bad
call is recorded and the run carries on rather than falling over.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from pashtobench.cache import CachingClient
from pashtobench.clients import client_for
from pashtobench.prompts import build_prompt
from pashtobench.schema import Item, find_jsonl, iter_jsonl, parse_line


@dataclass
class RunRecord:
    item_id: str
    model: str
    output: str
    cached: bool
    error: str = ""


def load_task_items(task: str, data_dir: str | Path = "data") -> list[Item]:
    root = Path(data_dir) / task
    items: list[Item] = []
    for path in find_jsonl(root):
        for _lineno, raw in iter_jsonl(path):
            items.append(parse_line(raw))
    return items


def run_task(
    task: str,
    model_names: list[str],
    data_dir: str | Path = "data",
    results_dir: str | Path = "results",
    client_factory=client_for,
    limit: int | None = None,
) -> list[RunRecord]:
    items = load_task_items(task, data_dir)
    if limit is not None:
        items = items[:limit]

    results_dir = Path(results_dir)
    records: list[RunRecord] = []
    for name in model_names:
        caching = CachingClient(
            client_factory(name),
            name,
            cache_dir=results_dir / "raw",
            cost_log=results_dir / "cost_log.csv",
        )
        for item in items:
            prompt = build_prompt(item)
            try:
                response = caching.complete(item.id, prompt)
                records.append(RunRecord(item.id, name, response.text, response.cached))
            except Exception as exc:  # one bad call must not stop the whole run
                records.append(RunRecord(item.id, name, "", False, error=str(exc)))

    _write_outputs(task, results_dir, records)
    return records


def _write_outputs(task: str, results_dir: Path, records: list[RunRecord]) -> None:
    out_dir = results_dir / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{task}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


def add_run_parser(sub) -> None:
    parser = sub.add_parser("run", help="run a task against models, cached and resumable")
    parser.add_argument(
        "--task",
        required=True,
        choices=["translation", "qa", "instruction", "safety"],
    )
    parser.add_argument("--models", required=True, help="comma separated model names")
    parser.add_argument("--limit", type=int, default=None, help="only the first N items")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--results-dir", default="results")
    parser.set_defaults(func=_run_run)


def _run_run(args) -> int:
    names = [name.strip() for name in args.models.split(",") if name.strip()]
    if not names:
        print("no models given")
        return 1
    records = run_task(
        args.task,
        names,
        data_dir=args.data_dir,
        results_dir=args.results_dir,
        limit=args.limit,
    )
    done = sum(1 for r in records if not r.error)
    cached = sum(1 for r in records if r.cached)
    errors = sum(1 for r in records if r.error)
    print(f"{len(records)} calls: {done} ok ({cached} from cache), {errors} errors")
    if errors:
        first = next(r for r in records if r.error)
        print(f"first error ({first.model}): {first.error}")
    return 0
