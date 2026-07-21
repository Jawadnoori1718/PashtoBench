import pytest

from pashtobench.scorers.qa import exact_match, score_qa, token_f1


def test_exact_match_identical():
    assert exact_match("کابل", "کابل") is True


def test_exact_match_ignores_punctuation():
    assert exact_match("کابل.", "کابل") is True
    assert exact_match("Kabul, Afghanistan", "Kabul Afghanistan") is True


def test_exact_match_folds_digits():
    # persian digits vs ascii, the normaliser folds them so it matches
    assert exact_match("۱۹۴۷", "1947") is True


def test_exact_match_different_is_false():
    assert exact_match("کابل", "هرات") is False


def test_token_f1_bounds():
    assert token_f1("a b c", "a b c") == pytest.approx(1.0)
    assert token_f1("a b c d", "e f g h") == pytest.approx(0.0)


def test_token_f1_partial_overlap():
    # pred has 2 of 3 reference tokens, and 3 predicted
    score = token_f1("the big house", "the small house")
    # overlap 2, precision 2/3, recall 2/3, f1 2/3
    assert score == pytest.approx(2 / 3, abs=0.001)


def test_score_qa_aggregates():
    preds = ["کابل", "1947", "wrong"]
    refs = ["کابل.", "۱۹۴۷", "right"]
    score = score_qa(preds, refs)
    assert score.n == 3
    # first two match exactly, third does not
    assert score.exact_match == pytest.approx(2 / 3, abs=0.001)
    assert 0.0 <= score.token_f1 <= 1.0


def test_score_qa_empty():
    assert score_qa([], []).n == 0


def test_score_qa_mismatched_lengths():
    with pytest.raises(ValueError, match="line up"):
        score_qa(["a"], ["a", "b"])
