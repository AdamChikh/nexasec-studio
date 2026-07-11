from nexasec.core.text_correction import apply_glossary


def test_normalizes_python_casing():
    assert apply_glossary("nta3lmou python lyoum") == "nta3lmou Python lyoum"


def test_normalizes_multiple_terms_in_one_sentence():
    text = "hadi function fiha loop, khdemna b python"
    result = apply_glossary(text)
    assert "function" in result
    assert "loop" in result
    assert "Python" in result


def test_does_not_corrupt_substrings():
    # "python" inside "pythonic" should NOT be replaced -- word
    # boundaries matter, this must not become "Pythonic"
    assert apply_glossary("pythonic style") == "pythonic style"


def test_case_insensitive_matching():
    assert apply_glossary("PYTHON") == "Python"
    assert apply_glossary("PyThOn") == "Python"


def test_leaves_arabic_text_untouched():
    arabic = "مرحبا بكم في الدرس اليوم"
    assert apply_glossary(arabic) == arabic


def test_idempotent():
    text = "we use python and Docker"
    once = apply_glossary(text)
    twice = apply_glossary(once)
    assert once == twice


def test_multi_word_term():
    assert apply_glossary("open vs code now") == "open VS Code now"
