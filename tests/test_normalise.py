import unicodedata

from pashtobench.normalise import PRESERVE, normalise


def test_empty_string():
    assert normalise("") == ""


def test_idempotent():
    text = "دا زما کور دی"
    once = normalise(text)
    assert normalise(once) == once


def test_zwnj_invariance():
    zwnj = "‌"
    assert normalise("کور" + zwnj + "ونه") == normalise("کورونه")


def test_yeh_forms_fold_to_farsi_yeh():
    farsi_yeh = "ی"
    assert normalise("ي") == farsi_yeh  # arabic yeh
    assert normalise("ى") == farsi_yeh  # alef maksura


def test_kaf_folds_to_keheh():
    assert normalise("ك") == "ک"


def test_digits_fold_to_ascii():
    assert normalise("٦٧") == "67"  # arabic indic
    assert normalise("۱۹۴۷") == "1947"  # persian


def test_tatweel_removed():
    assert normalise("کـــور") == "کور"


def test_harakat_removed():
    assert normalise("کَور") == "کور"


def test_preserved_letters_survive():
    for cp in PRESERVE:
        letter = chr(cp)
        assert letter in normalise(letter), f"lost {cp:04x}"


def test_gaf_not_folded_to_kaf():
    gaf = "گ"
    assert gaf in normalise(gaf)


def test_yeh_with_hamza_stays_atomic():
    # NFKD would split this into two codepoints, so I guard against it
    atomic = "ئ"
    result = normalise(atomic)
    assert result == atomic
    assert len(result) == 1


def test_preserve_never_folded_away():
    from pashtobench.normalise import _TABLE

    for cp in PRESERVE:
        assert cp not in _TABLE


def test_whitespace_collapsed():
    assert normalise("کور    دی") == "کور دی"
    assert normalise("  کور دی  ") == "کور دی"


def test_result_is_nfc():
    result = normalise("کور دی")
    assert result == unicodedata.normalize("NFC", result)
