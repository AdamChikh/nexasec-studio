from nexasec.core.bidi_formatter import wrap_ltr_runs, contains_rtl, LRI, PDI


def test_wraps_single_english_word_in_arabic_sentence():
    text = "نتعلمو loop اليوم"
    result = wrap_ltr_runs(text)
    assert f"{LRI}loop{PDI}" in result
    assert "نتعلمو" in result
    assert "اليوم" in result


def test_wraps_multiple_english_terms_separately():
    text = "hadi function fiha loop"
    result = wrap_ltr_runs(text)
    assert f"{LRI}function{PDI}" in result
    assert f"{LRI}loop{PDI}" in result


def test_pure_arabic_text_unchanged():
    arabic = "مرحبا بكم في الدرس"
    assert wrap_ltr_runs(arabic) == arabic


def test_keeps_dotted_code_terms_as_one_run():
    text = "استعملو requests.get() هنا"
    result = wrap_ltr_runs(text)
    assert f"{LRI}requests.get(){PDI}" in result


def test_contains_rtl_detects_arabic():
    assert contains_rtl("مرحبا") is True
    assert contains_rtl("hello") is False
    assert contains_rtl("hello مرحبا") is True
