import json
from argparse import Namespace

from pashtobench.validate import run_validate

VALID = {
    "id": "pbt-qa-001",
    "task": "qa",
    "lang": "pbt",
    "prompt": "پوښتنه",
    "reference": "ځواب",
    "domain": "civic",
    "difficulty": "easy",
}


def test_empty_dir_is_ok(tmp_path):
    assert run_validate(Namespace(path=str(tmp_path))) == 0


def test_valid_file_passes(tmp_path):
    f = tmp_path / "pbt.jsonl"
    f.write_text(json.dumps(VALID) + "\n", encoding="utf-8")
    assert run_validate(Namespace(path=str(f))) == 0


def test_broken_line_fails(tmp_path):
    f = tmp_path / "pbt.jsonl"
    f.write_text("{not json\n", encoding="utf-8")
    assert run_validate(Namespace(path=str(f))) == 1


def test_duplicate_across_lines_fails(tmp_path):
    f = tmp_path / "pbt.jsonl"
    f.write_text(json.dumps(VALID) + "\n" + json.dumps(VALID) + "\n", encoding="utf-8")
    assert run_validate(Namespace(path=str(f))) == 1
