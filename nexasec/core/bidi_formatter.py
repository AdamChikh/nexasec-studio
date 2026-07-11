import re


# Unicode directional isolate marks. Wrapping each Latin-script run
# in LRI/PDI tells any bidi-aware renderer "this specific chunk reads
# left-to-right, everything around it can still flow right-to-left" --
# the standard fix for embedding English words/code terms inside
# Arabic sentences without the whole line's direction getting
# scrambled.
LRI = "\u2066"  # Left-to-Right Isolate
PDI = "\u2069"  # Pop Directional Isolate

# Matches runs of Latin letters/digits, plus the punctuation that
# commonly appears inside code-like terms (dots, underscores,
# parentheses, hyphens) so "requests.get()" or "snake_case" stays
# one isolated run instead of getting split mid-token.
_LATIN_RUN = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9_.\-()]*[A-Za-z0-9)])?"
)


def wrap_ltr_runs(text: str) -> str:
    """
    Wrap every Latin-script run in a (likely Arabic) string with
    Unicode directional isolates, so subtitle renderers apply the
    bidi algorithm correctly instead of scrambling word order.

    Pure text-in-text-out Arabic strings without any Latin content
    are returned unchanged.
    """

    def _wrap(match: re.Match) -> str:
        return f"{LRI}{match.group(0)}{PDI}"

    return _LATIN_RUN.sub(_wrap, text)


def contains_rtl(text: str) -> bool:
    """
    True if the string contains any Arabic-script characters.
    """

    return any(
        "\u0600" <= ch <= "\u06FF" or "\u0750" <= ch <= "\u077F"
        for ch in text
    )
