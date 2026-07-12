from pathlib import Path
import subprocess

import pytest

from nexasec.core.clip import create_clip
from nexasec.core.clip_store import load_clip, clip_video_path
from nexasec.services.clip_attacher import attach_video, attach_audio
from nexasec.services.clip_syncer import sync_clip


def test_sync_clip_sets_synced_file(isolated_cwd, test_video, test_audio):

    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))
    attach_audio("lesson-001", "1.1", str(test_audio))

    output, offset = sync_clip("lesson-001", "1.1")

    assert output.exists()
    # test_audio was extracted directly from test_video with no
    # padding, so auto-detected offset should be ~0
    assert abs(offset) < 0.1

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


def test_sync_clip_auto_detects_real_offset(isolated_cwd, test_video, test_audio, tmp_path):
    """
    End-to-end proof that a deliberately-offset external audio file
    (like Adam's real 1.1.wav being much longer than 1.1.mov) gets
    correctly detected and trimmed -- not just that the underlying
    cross-correlation math works on synthetic signals (see
    test_audio_aligner.py), but that the full clip-sync pipeline
    actually uses it correctly.
    """

    # Build the 3s of silence as its OWN bounded file first (-t here
    # is the only output constraint on this command, so it's
    # guaranteed correct) -- then concat two already-fixed-duration
    # files via the concat demuxer. Trying to bound an infinite
    # anullsrc source inside a single -filter_complex concat command
    # does NOT reliably respect -t and can produce a runaway output.
    silence_path = tmp_path / "silence.wav"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=16000",
            "-t", "3",
            "-ar", "16000", "-ac", "1", "-sample_fmt", "s16",
            str(silence_path),
        ],
        check=True,
        capture_output=True,
    )

    concat_list = tmp_path / "concat_list.txt"
    concat_list.write_text(
        f"file '{silence_path}'\nfile '{Path(test_audio).resolve()}'\n"
    )

    padded_audio = tmp_path / "padded.wav"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(padded_audio),
        ],
        check=True,
        capture_output=True,
    )

    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))
    attach_audio("lesson-001", "1.1", str(padded_audio))

    output, detected_offset = sync_clip("lesson-001", "1.1")

    assert abs(detected_offset - 3.0) < 0.1
    assert output.exists()

    metadata = load_clip("lesson-001", "1.1")
    # duration should reflect the correctly-trimmed alignment, not
    # be thrown off by the 3s of leading silence
    assert metadata.video.duration is not None
    assert metadata.video.duration > 0


def test_sync_clip_manual_offset_override(isolated_cwd, test_video, test_audio):

    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))
    attach_audio("lesson-001", "1.1", str(test_audio))

    output, used_offset = sync_clip("lesson-001", "1.1", audio_offset=1.5)

    assert used_offset == 1.5
    assert output.exists()
