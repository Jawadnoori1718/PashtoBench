"""Render results/scores/*.json into results/leaderboard.md.

One markdown table per task, rows sorted by chrF++, with the sacrebleu
signature shown once so the numbers stay reproducible.
"""

import json
from pathlib import Path


def _task_table(data: dict) -> list[str]:
    task = data.get("task", "task")
    scores = sorted(data.get("scores", []), key=lambda row: row.get("chrf", 0), reverse=True)
    lines = [
        f"## {task.capitalize()}",
        "",
        "| Model | Direction | chrF++ | BLEU | n |",
        "|---|---|---|---|---|",
    ]
    for row in scores:
        lines.append(
            f"| {row['model']} | {row['direction']} | "
            f"{row['chrf']:.1f} | {row['bleu']:.1f} | {row['n']} |"
        )
    lines.append("")
    if scores:
        lines.append(f"Signature: `{scores[0]['chrf_signature']}`")
        lines.append("")
    return lines


def build_leaderboard(results_dir: str | Path = "results") -> str:
    results_dir = Path(results_dir)
    scores_dir = results_dir / "scores"
    files = sorted(scores_dir.glob("*.json")) if scores_dir.exists() else []

    lines = [
        "# PashtoBench leaderboard",
        "",
        "Auto generated from results/scores. chrF++ is the headline metric.",
        "",
    ]
    if not files:
        lines.append("No scores yet. Run a task and score it first.")
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        lines.extend(_task_table(data))

    markdown = "\n".join(lines) + "\n"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "leaderboard.md").write_text(markdown, encoding="utf-8")
    return markdown
