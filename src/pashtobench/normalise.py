"""Pashto text normaliser used before exact match and token F1 scoring.

I fold only the Arabic and Persian letter variants that Pashto writers use
interchangeably, and I keep every letter that carries a Pashto phoneme. The
full rationale lives in docs/METHODOLOGY.md section 2.
"""

import unicodedata

# I fold the interchangeable yeh forms to Farsi yeh.
_YEH = {0x064A: 0x06CC, 0x0649: 0x06CC}

# Arabic kaf folds to keheh, the Afghan standard.
_KAF = {0x0643: 0x06A9}

# heh goal folds to plain heh when it turns up.
_HEH = {0x06C1: 0x0647}

# Arabic Indic and Persian digits fold to ASCII by value.
_DIGITS = {}
for _i in range(10):
    _DIGITS[0x0660 + _i] = ord("0") + _i
    _DIGITS[0x06F0 + _i] = ord("0") + _i

_FOLD = {**_YEH, **_KAF, **_HEH, **_DIGITS}

# tatweel is cosmetic elongation with no sound.
_TATWEEL = {0x0640}

# zero width and bidi controls I strip out.
_CONTROLS = {
    0x200B,
    0x200C,
    0x200D,
    0x200E,
    0x200F,
    0x061C,
    0x00AD,
    0xFEFF,
    0x202A,
    0x202B,
    0x202C,
    0x202D,
    0x202E,
    0x2066,
    0x2067,
    0x2068,
    0x2069,
}

# harakat and the dagger alef, removed after NFC has composed the letters.
_HARAKAT = set(range(0x064B, 0x0653)) | {0x0670}

# Pashto letters I must never fold away, each a distinct phoneme or contrast.
PRESERVE = frozenset(
    {
        0x067C,  # tte
        0x0689,  # ddal
        0x0693,  # rre
        0x06BC,  # noon with ring
        0x069A,  # xin
        0x0696,  # ghin
        0x0681,  # dze
        0x0685,  # tse
        0x06D0,  # e
        0x06CD,  # yeh with tail
        0x0626,  # yeh with hamza
        0x06D2,  # yeh barree
    }
)

_REMOVE = _TATWEEL | _CONTROLS | _HARAKAT

# one translate table does the removals and the folds in a single pass.
_TABLE: dict[int, int | None] = {cp: None for cp in _REMOVE}
_TABLE.update(_FOLD)


def normalise(text: str) -> str:
    """Return the canonical form of a Pashto string for scoring."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.translate(_TABLE)
    text = " ".join(text.split())
    return unicodedata.normalize("NFC", text)
