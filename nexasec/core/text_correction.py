import re


# Canonical casing for programming terms that must stay in English
# inside Darija sentences, per the brand brief (loop, function, class,
# Python, etc. are never translated -- but WhisperX may transcribe
# them in lowercase, or with inconsistent casing, since it has no
# concept of "this word matters"). This is casing normalization only.
#
# NOTE: this is deliberately NOT a large dictionary of "fixes for
# Darija speech-to-text mistakes" -- that would require real observed
# transcription errors to be grounded in anything, and none exist yet.
# This glossary is meant to be extended over time as real corrections
# are observed in actual lesson transcripts.
DEFAULT_GLOSSARY = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "sql": "SQL",
    "docker": "Docker",
    "git": "Git",
    "github": "GitHub",
    "function": "function",
    "loop": "loop",
    "variable": "variable",
    "class": "class",
    "api": "API",
    "json": "JSON",
    "html": "HTML",
    "css": "CSS",
    "vscode": "VS Code",
    "vs code": "VS Code",
}


def apply_glossary(text: str, glossary: dict[str, str] | None = None) -> str:
    """
    Replace known programming terms with their canonical casing,
    matching whole words only (case-insensitive), so it doesn't
    corrupt Arabic text or unrelated substrings.
    """

    glossary = glossary if glossary is not None else DEFAULT_GLOSSARY

    result = text

    # Longest terms first so "vs code" matches before a lone "vs"
    # would ever be considered (not in this glossary today, but
    # keeps the ordering rule explicit for future entries).
    for term in sorted(glossary, key=len, reverse=True):

        pattern = re.compile(
            r"(?<![\w])" + re.escape(term) + r"(?![\w])",
            re.IGNORECASE
        )

        result = pattern.sub(glossary[term], result)

    return result
