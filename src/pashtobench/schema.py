"""Item schema and the checks the validator runs over a data file.

Every item across the four tasks shares one flat shape. The task specific
fields are optional on the model and a validator enforces the ones each task
needs. The schema is described in docs/PROJECT_CHARTER.md and the tasks in
docs/METHODOLOGY.md.
"""

import json
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

Task = Literal["translation", "qa", "instruction", "safety"]
Lang = Literal["pbt", "en"]
Domain = Literal["daily_life", "culture", "civic", "technical"]
Difficulty = Literal["easy", "medium", "hard"]
Direction = Literal["en-pbt", "pbt-en"]
SafetyArm = Literal["sensitive", "benign"]


class Item(BaseModel):
    """One benchmark item. Extra fields are rejected to catch typos early."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    task: Task
    lang: Lang
    prompt: str = Field(min_length=1)
    domain: Domain
    difficulty: Difficulty
    author_verified: bool = False
    second_verifier: bool = False
    en_anchor_id: str | None = None
    cultural_note: str | None = None

    # translation only
    direction: Direction | None = None
    reference: str | None = None

    # instruction following only
    instruction_ids: list[str] | None = None
    kwargs: list[dict] | None = None

    # safety only
    arm: SafetyArm | None = None
    category: str | None = None
    provenance: str | None = None

    @model_validator(mode="after")
    def _check_task_fields(self) -> "Item":
        if self.task == "translation":
            if self.direction is None:
                raise ValueError("translation item needs a direction")
            if not self.reference:
                raise ValueError("translation item needs a reference")
        elif self.task == "qa":
            if not self.reference:
                raise ValueError("qa item needs a reference")
        elif self.task == "instruction":
            if not self.instruction_ids:
                raise ValueError("instruction item needs instruction_ids")
            if self.kwargs is not None and len(self.kwargs) != len(self.instruction_ids):
                raise ValueError("kwargs must line up with instruction_ids")
        elif self.task == "safety":
            if self.arm is None:
                raise ValueError("safety item needs an arm")
            if not self.provenance:
                raise ValueError("safety item needs a provenance note")
        return self


def parse_line(raw: str) -> Item:
    """Parse one JSONL line into an Item, with a readable error on failure."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"not valid json: {exc.msg}") from exc
    try:
        return Item.model_validate(data)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(p) for p in first["loc"]) or "item"
        raise ValueError(f"{where}: {first['msg']}") from exc


def iter_jsonl(path: Path) -> Iterator[tuple[int, str]]:
    """Yield the line number and text of each non empty line in a file."""
    with path.open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            if line.strip():
                yield lineno, line


def find_jsonl(root: Path) -> list[Path]:
    """Return the jsonl files under a directory, or the file itself."""
    if root.is_file():
        return [root]
    return sorted(root.rglob("*.jsonl"))


def duplicate_id_errors(items: list[Item]) -> list[str]:
    """Report any id that appears more than once."""
    counts = Counter(item.id for item in items)
    return [f"duplicate id: {item_id}" for item_id, n in counts.items() if n > 1]


def dangling_anchor_warnings(items: list[Item]) -> list[str]:
    """Report anchors that point at an id not present in the loaded set."""
    ids = {item.id for item in items}
    warnings = []
    for item in items:
        if item.en_anchor_id and item.en_anchor_id not in ids:
            warnings.append(f"{item.id}: anchor {item.en_anchor_id} not found")
    return warnings
