import json

from pashtobench.clients import ModelResponse
from pashtobench.prompts import build_prompt
from pashtobench.runner import load_task_items, run_task
from pashtobench.schema import Item

TR_EN = {
    "id": "pbt-tr-001",
    "task": "translation",
    "lang": "pbt",
    "direction": "en-pbt",
    "prompt": "The house is big.",
    "reference": "کور لوی دی.",
    "domain": "daily_life",
    "difficulty": "easy",
    "author_verified": True,
    "second_verifier": False,
}
TR_PBT = {
    "id": "pbt-tr-002",
    "task": "translation",
    "lang": "pbt",
    "direction": "pbt-en",
    "prompt": "زه ښوونځي ته ځم.",
    "reference": "I go to school.",
    "domain": "daily_life",
    "difficulty": "easy",
    "author_verified": True,
    "second_verifier": False,
}


def _write_data(tmp_path, rows):
    task_dir = tmp_path / "data" / "translation"
    task_dir.mkdir(parents=True)
    with (task_dir / "pbt.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return tmp_path / "data"


class EchoClient:
    """A stand in that echoes the prompt and counts real calls."""

    def __init__(self):
        self.calls = 0

    def complete(self, prompt, system=None):
        self.calls += 1
        return ModelResponse(text=f"reply:{prompt[:8]}", model="echo", output_tokens=1)


def test_build_prompt_translation_directions():
    en = Item.model_validate(TR_EN)
    pbt = Item.model_validate(TR_PBT)
    assert "into Pashto" in build_prompt(en)
    assert build_prompt(en).endswith("The house is big.")
    assert "into English" in build_prompt(pbt)


def test_load_task_items(tmp_path):
    data_dir = _write_data(tmp_path, [TR_EN, TR_PBT])
    items = load_task_items("translation", data_dir=data_dir)
    assert [i.id for i in items] == ["pbt-tr-001", "pbt-tr-002"]


def test_run_produces_records_and_outputs(tmp_path):
    data_dir = _write_data(tmp_path, [TR_EN, TR_PBT])
    results_dir = tmp_path / "results"
    factory = lambda name: EchoClient()  # noqa: E731

    records = run_task(
        "translation",
        ["m1", "m2"],
        data_dir=data_dir,
        results_dir=results_dir,
        client_factory=factory,
    )
    # two models times two items
    assert len(records) == 4
    assert all(not r.error for r in records)

    out = results_dir / "outputs" / "translation.jsonl"
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 4


def test_second_run_is_cached(tmp_path):
    data_dir = _write_data(tmp_path, [TR_EN])
    results_dir = tmp_path / "results"
    client = EchoClient()
    factory = lambda name: client  # noqa: E731

    run_task(
        "translation", ["m1"], data_dir=data_dir, results_dir=results_dir, client_factory=factory
    )
    assert client.calls == 1

    records = run_task(
        "translation", ["m1"], data_dir=data_dir, results_dir=results_dir, client_factory=factory
    )
    assert client.calls == 1  # served from cache, no new call
    assert records[0].cached is True


def test_error_is_recorded_and_run_continues(tmp_path):
    data_dir = _write_data(tmp_path, [TR_EN, TR_PBT])
    results_dir = tmp_path / "results"

    class Boom:
        def complete(self, prompt, system=None):
            raise RuntimeError("no api key")

    records = run_task(
        "translation",
        ["broken"],
        data_dir=data_dir,
        results_dir=results_dir,
        client_factory=lambda name: Boom(),
    )
    assert len(records) == 2
    assert all(r.error for r in records)
    assert "no api key" in records[0].error
