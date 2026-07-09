import pytest

from nexasec.core.clip import create_clip
from nexasec.core.clip_store import (
    clip_exists,
    load_clip,
    save_clip,
)


def test_load_clip_after_create(isolated_cwd):

    create_clip("lesson-001", "1.1")

    metadata = load_clip("lesson-001", "1.1")

    assert metadata.name == "1.1"


def test_clip_exists(isolated_cwd):

    assert clip_exists("lesson-001", "1.1") is False

    create_clip("lesson-001", "1.1")

    assert clip_exists("lesson-001", "1.1") is True


def test_load_missing_clip_raises_helpful_error(isolated_cwd):

    with pytest.raises(FileNotFoundError, match="does not exist"):
        load_clip("lesson-001", "does-not-exist")


def test_save_clip_persists_changes(isolated_cwd):

    create_clip("lesson-001", "1.1")

    metadata = load_clip("lesson-001", "1.1")
    metadata.status = "imported"
    save_clip("lesson-001", "1.1", metadata)

    reloaded = load_clip("lesson-001", "1.1")
    assert reloaded.status == "imported"
