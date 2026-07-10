"""The `pashtobench validate` command.

I load every item, check each against the schema, then run collection checks
for duplicate ids and dangling anchors. Hard errors fail the command so CI
can gate on it; dangling anchors are warnings while the data is partial.
"""

from argparse import _SubParsersAction
from pathlib import Path

from pashtobench.schema import (
    Item,
    dangling_anchor_warnings,
    duplicate_id_errors,
    find_jsonl,
    iter_jsonl,
    parse_line,
)


def add_validate_parser(sub: _SubParsersAction) -> None:
    parser = sub.add_parser("validate", help="check data items against the schema")
    parser.add_argument(
        "path",
        nargs="?",
        default="data",
        help="a data directory or a single jsonl file",
    )
    parser.set_defaults(func=run_validate)


def run_validate(args) -> int:
    root = Path(args.path)
    files = find_jsonl(root)
    if not files:
        print(f"no jsonl items found under {root}")
        return 0

    items: list[Item] = []
    errors: list[str] = []
    for path in files:
        for lineno, raw in iter_jsonl(path):
            try:
                items.append(parse_line(raw))
            except ValueError as exc:
                errors.append(f"{path}:{lineno}: {exc}")

    errors.extend(duplicate_id_errors(items))
    warnings = dangling_anchor_warnings(items)

    for warning in warnings:
        print(f"warning: {warning}")

    if errors:
        for error in errors:
            print(f"error: {error}")
        print(f"\n{len(items)} items checked, {len(errors)} errors")
        return 1

    print(f"{len(items)} items valid across {len(files)} files")
    return 0
