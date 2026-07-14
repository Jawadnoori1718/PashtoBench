import pytest

from pashtobench.scorers.translation import score_by_direction, score_corpus


def test_identical_corpus_scores_100():
    refs = ["the cat sat on the mat", "i walk to the school every morning"]
    score = score_corpus(refs, refs)
    assert score.chrf == pytest.approx(100.0, abs=0.01)
    assert score.bleu == pytest.approx(100.0, abs=0.01)
    assert score.n == 2


def test_signatures_carry_the_metric_settings():
    score = score_corpus(["hello world"], ["hello world"])
    assert "chrF2++" in score.chrf_signature
    assert "nw:2" in score.chrf_signature  # word order 2 = chrF++
    assert "nc:6" in score.chrf_signature  # character order 6
    assert "tok:intl" in score.bleu_signature  # not the default 13a


def test_worse_hypothesis_scores_lower():
    ref = ["the quick brown fox jumps over the lazy dog"]
    good = score_corpus(["the quick brown fox jumps over the lazy dog"], ref)
    poor = score_corpus(["a slow green turtle"], ref)
    assert poor.chrf < good.chrf


def test_normaliser_is_applied_before_scoring():
    # the two strings differ only by arabic yeh vs farsi yeh, which the
    # normaliser folds together, so the score must be perfect
    hyp = ["دی"]  # farsi yeh
    ref = ["دي"]  # arabic yeh
    assert score_corpus(hyp, ref).chrf == pytest.approx(100.0, abs=0.01)


def test_score_by_direction_splits_the_corpora():
    records = [
        ("کور لوی دی", "کور لوی دی", "en-pbt"),
        ("i go to school", "i go to school", "pbt-en"),
    ]
    scores = score_by_direction(records)
    assert set(scores) == {"en-pbt", "pbt-en"}
    assert scores["en-pbt"].n == 1
    assert scores["pbt-en"].chrf == pytest.approx(100.0, abs=0.01)
