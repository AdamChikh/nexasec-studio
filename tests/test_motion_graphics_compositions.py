from html.parser import HTMLParser
from pathlib import Path
import json
import re

import pytest


COMPOSITIONS_DIR = Path("motion-graphics/compositions")

REQUIRED_VARIABLE_FIELDS = ("id", "type", "label", "default")
VALID_VARIABLE_TYPES = ("string", "number", "color", "boolean", "enum")


class _TagBalanceChecker(HTMLParser):

    VOID_TAGS = {"meta", "link", "br", "img", "input", "hr"}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.mismatches = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.mismatches.append(tag)
        else:
            self.stack.pop()


def _all_composition_files():
    if not COMPOSITIONS_DIR.exists():
        return []
    return sorted(COMPOSITIONS_DIR.glob("*.html"))


@pytest.mark.parametrize("path", _all_composition_files(), ids=lambda p: p.name)
def test_composition_html_tags_are_balanced(path):

    checker = _TagBalanceChecker()
    checker.feed(path.read_text(encoding="utf-8"))

    assert checker.stack == [], f"{path.name}: unclosed tags {checker.stack}"
    assert checker.mismatches == [], f"{path.name}: mismatched tags {checker.mismatches}"


@pytest.mark.parametrize("path", _all_composition_files(), ids=lambda p: p.name)
def test_composition_variables_json_is_valid(path):

    content = path.read_text(encoding="utf-8")
    match = re.search(r"data-composition-variables='(\[.*?\])'", content, re.DOTALL)

    if match is None:
        pytest.skip(f"{path.name} declares no data-composition-variables")

    variables = json.loads(match.group(1))  # raises if malformed

    for variable in variables:
        for field in REQUIRED_VARIABLE_FIELDS:
            assert field in variable, (
                f"{path.name}: variable {variable} missing required "
                f"field '{field}'"
            )
        assert variable["type"] in VALID_VARIABLE_TYPES, (
            f"{path.name}: variable '{variable['id']}' has unknown "
            f"type '{variable['type']}'"
        )


@pytest.mark.parametrize("path", _all_composition_files(), ids=lambda p: p.name)
def test_composition_registers_a_gsap_timeline(path):
    """
    Every composition should register itself on window.__timelines --
    a composition that forgets this silently produces a static (or
    broken) render with no animation.
    """

    content = path.read_text(encoding="utf-8")
    assert "window.__timelines" in content, (
        f"{path.name} does not register a GSAP timeline on "
        f"window.__timelines"
    )
