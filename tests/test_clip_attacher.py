import pytest

from nexasec.core.clip import create_clip
from nexasec.core.clip_store import load_clip
from nexasec.services.clip_attacher import attach, attach_video, attach_audio


def test_attach_video_populates_metadata(isolated_cwd, test_video):

    create_clip("lesson-001", "1.1")

    destination = attach_video("lesson-001", "1.1", str(test_video))

    assert destination.exists()

    metadata = load_clip("lesson-001", "1.1")

    assert metadata.status == "imported"
    assert metadata.video.file == test_video.name
    assert metadata.video.width is not None
    assert metadata.video.height is not None
    assert metadata.video.duration is not None
    assert metadata.video.codec is not None


def test_attach_audio_populates_metadata(isolated_cwd, test_audio):

    create_clip("lesson-001", "1.1")

    destination = attach_audio("lesson-001", "1.1", str(test_audio))

    assert destination.exists()

    metadata = load_clip("lesson-001", "1.1")

    assert metadata.audio.file == test_audio.name
    assert metadata.audio.type == "microphone"


def test_attach_dispatches_by_media_type(isolated_cwd, test_video, test_audio):

    create_clip("lesson-001", "1.1")

    attach("lesson-001", "1.1", "video", str(test_video))
    attach("lesson-001", "1.1", "audio", str(test_audio))

    metadata = load_clip("lesson-001", "1.1")

    assert metadata.video.file == test_video.name
    assert metadata.audio.file == test_audio.name


def test_attach_unsupported_media_type_raises(isolated_cwd, test_video):

    create_clip("lesson-001", "1.1")

    with pytest.raises(ValueError, match="Unsupported media type"):
        attach("lesson-001", "1.1", "image", str(test_video))


def test_attach_missing_clip_raises(isolated_cwd, test_video):

    with pytest.raises(FileNotFoundError, match="does not exist"):
        attach_video("lesson-001", "does-not-exist", str(test_video))


def test_attach_missing_source_file_raises(isolated_cwd):

    create_clip("lesson-001", "1.1")

    with pytest.raises(FileNotFoundError):
        attach_video("lesson-001", "1.1", "no-such-file.mov")
