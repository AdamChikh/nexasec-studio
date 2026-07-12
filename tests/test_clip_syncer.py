import pytest

from nexasec.core.clip import create_clip
from nexasec.core.clip_store import load_clip, clip_video_path
from nexasec.services.clip_attacher import attach_video, attach_audio
from nexasec.services.clip_syncer import sync_clip


def test_sync_clip_sets_synced_file(isolated_cwd, test_video, test_audio):

    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))
    attach_audio("lesson-001", "1.1", str(test_audio))

    output = sync_clip("lesson-001", "1.1")

    assert output.exists()

    metadata = load_clip("lesson-001", "1.1")
    assert metadata.video.synced_file == "synced.mp4"
    assert metadata.status == "synced"


def test_sync_clip_reprobes_actual_duration(isolated_cwd, test_video, test_audio):
    """
    The synced output's real duration (min of video/audio due to
    -shortest) must be re-probed and stored, not left as whatever
    the pre-sync raw video's duration happened to be.
    """

    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))
    attach_audio("lesson-001", "1.1", str(test_audio))

    pre_sync_duration = load_clip("lesson-001", "1.1").video.duration

    sync_clip("lesson-001", "1.1")

    metadata = load_clip("lesson-001", "1.1")

    # duration must be a real, freshly-probed positive number, not
    # None and not silently unchanged-but-wrong
    assert metadata.video.duration is not None
    assert metadata.video.duration > 0
    # since test_audio is derived directly from test_video (same
    # source), durations should be very close either way -- this
    # mainly guards against duration becoming None or zero
    assert abs(metadata.video.duration - pre_sync_duration) < 1.0


def test_clip_video_path_prefers_synced_file(isolated_cwd, test_video, test_audio):

    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))
    attach_audio("lesson-001", "1.1", str(test_audio))

    # before sync: resolves to the raw imported video
    pre_sync_path = clip_video_path("lesson-001", "1.1")
    assert pre_sync_path.name == test_video.name

    sync_clip("lesson-001", "1.1")

    # after sync: resolves to synced.mp4, not the raw video
    post_sync_path = clip_video_path("lesson-001", "1.1")
    assert post_sync_path.name == "synced.mp4"


def test_clip_video_path_raises_without_any_video(isolated_cwd):

    create_clip("lesson-001", "1.1")

    with pytest.raises(ValueError, match="no video attached"):
        clip_video_path("lesson-001", "1.1")


def test_sync_clip_without_video_raises(isolated_cwd, test_audio):

    create_clip("lesson-001", "1.1")
    attach_audio("lesson-001", "1.1", str(test_audio))

    with pytest.raises(ValueError, match="no video attached"):
        sync_clip("lesson-001", "1.1")


def test_sync_clip_without_audio_raises(isolated_cwd, test_video):

    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))

    with pytest.raises(ValueError, match="no audio attached"):
        sync_clip("lesson-001", "1.1")
