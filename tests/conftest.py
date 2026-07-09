from pathlib import Path
import os
import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def isolated_cwd(tmp_path, monkeypatch):
    """
    Most of nexasec's core/services resolve paths as
    Path("projects") / ... relative to the current working
    directory. Chdir into a throwaway tmp_path per test so tests
    never touch the real projects/ folder in the repo.
    """

    monkeypatch.chdir(tmp_path)

    return tmp_path


@pytest.fixture
def test_video() -> Path:
    return REPO_ROOT / "tests" / "assets" / "test-video.mp4"


@pytest.fixture
def test_audio() -> Path:
    return REPO_ROOT / "tests" / "assets" / "test-audio.wav"
