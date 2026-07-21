"""Factual QA scorers: exact match and token F1, on normalised text.

I normalise both sides (docs/METHODOLOGY.md section 2), strip punctuation so it
cannot leak into a mismatch, then compare. Token F1 is a multiset overlap over
whitespace tokens. Because the normaliser folds digits, a numeric answer matches
whether it is written in ASCII or Perso-Arabic digits.
"""

from collections import Counter
from dataclasses import dataclass

from pashtobench.normalise import normalise

# arabic and latin punctuation I strip before matching
_PUNCT = "،؛؟۔" + r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
_STRIP = str.maketrans("", "", _PUNCT)


def _tokens(text: str) -> list[str]:
    return normalise(text).translate(_STRIP).split()


def exact_match(prediction: str, reference: str) -> bool:
    return _tokens(prediction) == _tokens(reference)


def token_f1(prediction: str, reference: str) -> float:
    pred = _tokens(prediction)
    ref = _tokens(reference)
    if not pred and not ref:
        return 1.0
    if not pred or not ref:
        return 0.0
    overlap = sum((Counter(pred) & Counter(ref)).values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(pred)
    recall = overlap / len(ref)
    return 2 * precision * recall / (precision + recall)


@dataclass
class QAScore:
    n: int
    exact_match: float  # fraction of items matched
    token_f1: float  # mean token F1


def score_qa(predictions: list[str], references: list[str]) -> QAScore:
    if len(predictions) != len(references):
        raise ValueError("predictions and references must line up")
    n = len(predictions)
    if n == 0:
        return QAScore(n=0, exact_match=0.0, token_f1=0.0)
    em = sum(exact_match(p, r) for p, r in zip(predictions, references, strict=True))
    f1 = sum(token_f1(p, r) for p, r in zip(predictions, references, strict=True))
    return QAScore(n=n, exact_match=em / n, token_f1=f1 / n)
