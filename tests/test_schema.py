import json

import pytest

from pashtobench.schema import (
    Item,
    dangling_anchor_warnings,
    duplicate_id_errors,
    parse_line,
)

TRANSLATION = {
    "id": "pbt-tr-001",
    "task": "translation",
    "lang": "pbt",
    "direction": "en-pbt",
    "prompt": "Translate: the house is big.",
    "reference": "کور لوی دی",
    "en_anchor_id": "en-tr-001",
    "domain": "daily_life",
    "difficulty": "easy",
    "author_verified": True,
    "second_verifier": False,
}

QA = {
    "id": "pbt-qa-001",
    "task": "qa",
    "lang": "pbt",
    "prompt": "د افغانستان پلازمینه کومه ده؟",
    "reference": "کابل",
    "en_anchor_id": "en-qa-001",
    "domain": "civic",
    "difficulty": "easy",
}

INSTRUCTION = {
    "id": "pbt-if-001",
    "task": "instruction",
    "lang": "pbt",
    "prompt": "Answer in exactly two sentences.",
    "domain": "technical",
    "difficulty": "medium",
    "instruction_ids": ["length_constraints:number_sentences"],
    "kwargs": [{"num_sentences": 2, "relation": "at least"}],
}

SAFETY = {
    "id": "pbt-sf-001",
    "task": "safety",
    "lang": "pbt",
    "prompt": "A benign but tricky request.",
    "domain": "daily_life",
    "difficulty": "medium",
    "arm": "benign",
    "provenance": "adapted from a public benign contrast set",
}


def test_valid_items_parse():
    for data in (TRANSLATION, QA, INSTRUCTION, SAFETY):
        item = parse_line(json.dumps(data))
        assert isinstance(item, Item)


def test_translation_without_reference_fails():
    data = dict(TRANSLATION)
    del data["reference"]
    with pytest.raises(ValueError, match="reference"):
        parse_line(json.dumps(data))


def test_translation_without_direction_fails():
    data = dict(TRANSLATION)
    del data["direction"]
    with pytest.raises(ValueError, match="direction"):
        parse_line(json.dumps(data))


def test_safety_without_provenance_fails():
    data = dict(SAFETY)
    del data["provenance"]
    with pytest.raises(ValueError, match="provenance"):
        parse_line(json.dumps(data))


def test_instruction_kwargs_must_match():
    data = dict(INSTRUCTION)
    data["kwargs"] = []
    with pytest.raises(ValueError, match="line up"):
        parse_line(json.dumps(data))


def test_unknown_field_rejected():
    data = dict(QA)
    data["typo_field"] = "oops"
    with pytest.raises(ValueError):
        parse_line(json.dumps(data))


def test_bad_task_rejected():
    data = dict(QA)
    data["task"] = "summarisation"
    with pytest.raises(ValueError):
        parse_line(json.dumps(data))


def test_bad_json_message():
    with pytest.raises(ValueError, match="not valid json"):
        parse_line("{not json")


def test_duplicate_ids_detected():
    a = parse_line(json.dumps(QA))
    b = parse_line(json.dumps(QA))
    assert duplicate_id_errors([a, b])


def test_dangling_anchor_warned():
    item = parse_line(json.dumps(QA))
    assert dangling_anchor_warnings([item])  # en-qa-001 is not present
