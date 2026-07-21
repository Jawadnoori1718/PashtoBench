import json

from pashtobench.leaderboard import build_leaderboard
from pashtobench.score import score_translation_run

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
    "prompt": "زه ښوونځي ته ځm.".replace("m.", "."),
    "reference": "I go to school.",
    "domain": "daily_life",
    "difficulty": "easy",
    "author_verified": True,
    "second_verifier": False,
}


def _rec(item_id, model, output, error=""):
    return {
        "item_id": item_id,
        "model": model,
        "output": output,
        "cached": False,
        "error": error,
    }


def _setup(tmp_path):
    data_dir = tmp_path / "data" / "translation"
    data_dir.mkdir(parents=True)
    with (data_dir / "pbt.jsonl").open("w", encoding="utf-8") as f:
        for row in (TR_EN, TR_PBT):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    out_dir = tmp_path / "results" / "outputs"
    out_dir.mkdir(parents=True)
    records = [
        # perfect model: output equals the reference
        _rec("pbt-tr-001", "good", TR_EN["reference"]),
        _rec("pbt-tr-002", "good", TR_PBT["reference"]),
        # weak model: wrong output
        _rec("pbt-tr-001", "weak", "ناسم"),
        _rec("pbt-tr-002", "weak", "wrong"),
    ]
    with (out_dir / "translation.jsonl").open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return tmp_path / "data", tmp_path / "results"


def test_score_run_writes_scores(tmp_path):
    data_dir, results_dir = _setup(tmp_path)
    payload = score_translation_run(data_dir=data_dir, results_dir=results_dir)

    # two models times two directions
    assert len(payload["scores"]) == 4
    good_en = next(
        s for s in payload["scores"] if s["model"] == "good" and s["direction"] == "en-pbt"
    )
    assert good_en["chrf"] > 99.9  # perfect output

    saved = json.loads((results_dir / "scores" / "translation.json").read_text(encoding="utf-8"))
    assert saved["task"] == "translation"


def test_score_run_skips_errors(tmp_path):
    data_dir, results_dir = _setup(tmp_path)
    # add an errored record that must be ignored
    out = results_dir / "outputs" / "translation.jsonl"
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(_rec("pbt-tr-001", "broken", "", error="no key")) + "\n")
    payload = score_translation_run(data_dir=data_dir, results_dir=results_dir)
    broken = [s for s in payload["scores"] if s["model"] == "broken"]
    # the only item for broken errored, so it has no scorable direction
    assert broken == [] or all(s["n"] == 0 for s in broken)


def test_leaderboard_renders_table(tmp_path):
    data_dir, results_dir = _setup(tmp_path)
    score_translation_run(data_dir=data_dir, results_dir=results_dir)
    markdown = build_leaderboard(results_dir=results_dir)

    assert "# PashtoBench leaderboard" in markdown
    assert "## Translation" in markdown
    assert "chrF++" in markdown
    assert "good" in markdown and "weak" in markdown
    assert "chrF2++" in markdown  # the signature line
    # the file was written
    assert (results_dir / "leaderboard.md").exists()


def test_leaderboard_empty_case(tmp_path):
    markdown = build_leaderboard(results_dir=tmp_path / "results")
    assert "No scores yet" in markdown
