"""Translation scorers: chrF++ primary, BLEU secondary, via sacrebleu.

I normalise both sides first (docs/METHODOLOGY.md section 2), score each
direction as its own corpus, and keep the full sacrebleu signature so every
number is reproducible. chrF++ is the headline; BLEU is a caveated second.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from sacrebleu.metrics import BLEU, CHRF

from pashtobench.normalise import normalise


@dataclass
class CorpusScore:
    direction: str
    n: int
    chrf: float
    bleu: float
    chrf_signature: str
    bleu_signature: str


def _chrf() -> CHRF:
    # word_order 2 turns plain chrF into chrF++.
    return CHRF(word_order=2)


def _bleu() -> BLEU:
    # the intl tokeniser handles Perso-Arabic punctuation; the default 13a does not.
    return BLEU(tokenize="intl")


def score_corpus(
    hypotheses: Sequence[str],
    references: Sequence[str],
    direction: str = "",
) -> CorpusScore:
    hyps = [normalise(h) for h in hypotheses]
    refs = [normalise(r) for r in references]
    chrf = _chrf()
    bleu = _bleu()
    chrf_result = chrf.corpus_score(hyps, [refs])
    bleu_result = bleu.corpus_score(hyps, [refs])
    return CorpusScore(
        direction=direction,
        n=len(hyps),
        chrf=chrf_result.score,
        bleu=bleu_result.score,
        chrf_signature=f"{chrf_result.name}|{chrf.get_signature().format()}",
        bleu_signature=f"{bleu_result.name}|{bleu.get_signature().format()}",
    )


def score_by_direction(
    records: Iterable[tuple[str, str, str]],
) -> dict[str, CorpusScore]:
    """Group (hypothesis, reference, direction) triples and score each direction."""
    groups: dict[str, tuple[list[str], list[str]]] = {}
    for hypothesis, reference, direction in records:
        hyps, refs = groups.setdefault(direction, ([], []))
        hyps.append(hypothesis)
        refs.append(reference)
    return {
        direction: score_corpus(hyps, refs, direction=direction)
        for direction, (hyps, refs) in groups.items()
    }
