import json

from nexasec.core.clip import create_clip
from nexasec.core.clip_store import clip_folder, load_clip, save_clip
from nexasec.core.project import create_project
from nexasec.core.timeline import build_timeline
from nexasec.services.caption_builder import (
    build_youtube_captions,
    build_shorts_captions,
)
from nexasec.core.bidi_formatter import LRI, PDI


def _write_transcript(project, clip_name, segments):

    path = clip_folder(project, clip_name) / "captions" / "raw" / "transcript.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"segments": segments}), encoding="utf-8")


def _make_ready_clip(project, name, duration, segments):
    """
    Create a clip, fake it into an imported+transcribed state with
    a fixture transcript, without needing real media/WhisperX.
    """

    create_clip(project, name)
    metadata = load_clip(project, name)
    metadata.video.file = f"{name}.mov"
    metadata.video.duration = duration
    metadata.status = "transcribed"
    save_clip(project, name, metadata)

    _write_transcript(project, name, segments)


def test_youtube_captions_shift_timestamps_by_clip_offset(isolated_cwd):

    create_project("lesson-001")

    _make_ready_clip(
        "lesson-001", "1.1", duration=5.0,
        segments=[{"start": 0.0, "end": 2.0, "text": "salam"}],
    )
    _make_ready_clip(
        "lesson-001", "2.1", duration=3.0,
        segments=[{"start": 0.0, "end": 1.5, "text": "welcome"}],
    )

    build_timeline("lesson-001")

    srt_path, ass_path, warnings = build_youtube_captions("lesson-001")

    assert warnings == []

    srt_content = srt_path.read_text()

    # clip 1.1 sits at timeline start 0.0, clip 2.1 starts at 5.0
    # (right after 1.1's 5s duration) -- its segment must be shifted
    assert "00:00:00,000 --> 00:00:02,000" in srt_content
    assert "00:00:05,000 --> 00:00:06,500" in srt_content


def test_youtube_captions_apply_glossary_correction(isolated_cwd):

    create_project("lesson-001")

    _make_ready_clip(
        "lesson-001", "1.1", duration=5.0,
        segments=[{"start": 0.0, "end": 2.0, "text": "nta3lmou python lyoum"}],
    )

    build_timeline("lesson-001")
    srt_path, _, _ = build_youtube_captions("lesson-001")

    assert "Python" in srt_path.read_text()


def test_youtube_captions_apply_rtl_ltr_wrapping_for_arabic_project(isolated_cwd):

    create_project("lesson-001")  # default language is ar-DZ

    _make_ready_clip(
        "lesson-001", "1.1", duration=5.0,
        segments=[{"start": 0.0, "end": 2.0, "text": "نتعلمو loop اليوم"}],
    )

    build_timeline("lesson-001")
    _, ass_path, _ = build_youtube_captions("lesson-001")

    content = ass_path.read_text()
    assert f"{LRI}loop{PDI}" in content


def test_youtube_captions_warns_on_missing_transcript(isolated_cwd):

    create_project("lesson-001")

    _make_ready_clip(
        "lesson-001", "1.1", duration=5.0,
        segments=[{"start": 0.0, "end": 2.0, "text": "salam"}],
    )

    # 2.1 has video but no transcript
    create_clip("lesson-001", "2.1")
    metadata = load_clip("lesson-001", "2.1")
    metadata.video.file = "2.1.mov"
    metadata.video.duration = 3.0
    save_clip("lesson-001", "2.1", metadata)

    build_timeline("lesson-001")
    srt_path, _, warnings = build_youtube_captions("lesson-001")

    assert len(warnings) == 1
    assert "2.1" in warnings[0]
    assert "salam" in srt_path.read_text()


def test_shorts_captions_produce_karaoke_tags(isolated_cwd):

    create_project("lesson-001")

    _make_ready_clip(
        "lesson-001", "1.1", duration=5.0,
        segments=[{
            "start": 0.0, "end": 1.0, "text": "hadi loop",
            "words": [
                {"word": "hadi", "start": 0.0, "end": 0.5},
                {"word": "loop", "start": 0.5, "end": 1.0},
            ],
        }],
    )

    output = build_shorts_captions("lesson-001", "1.1")
    content = output.read_text()

    assert r"{\k" in content
    assert "loop" in content


def test_shorts_captions_karaoke_words_get_bidi_wrapped_individually(isolated_cwd):

    create_project("lesson-001")

    _make_ready_clip(
        "lesson-001", "1.1", duration=5.0,
        segments=[{
            "start": 0.0, "end": 1.0, "text": "نتعلمو loop اليوم",
            "words": [
                {"word": "نتعلمو", "start": 0.0, "end": 0.3},
                {"word": "loop", "start": 0.3, "end": 0.6},
                {"word": "اليوم", "start": 0.6, "end": 1.0},
            ],
        }],
    )

    output = build_shorts_captions("lesson-001", "1.1")
    content = output.read_text()

    # the isolate marks must wrap only the English word, and the
    # {\k} tag syntax itself must stay intact (not have isolate
    # marks injected inside the braces)
    assert f"{LRI}loop{PDI}" in content
    assert r"{\k" in content
    assert f"{{\\k" + LRI not in content  # tag braces not corrupted


def test_shorts_captions_falls_back_to_plain_line_without_word_timestamps(isolated_cwd):

    create_project("lesson-001")

    _make_ready_clip(
        "lesson-001", "1.1", duration=5.0,
        segments=[{"start": 0.0, "end": 1.0, "text": "salam", "words": []}],
    )

    output = build_shorts_captions("lesson-001", "1.1")
    content = output.read_text()

    assert "salam" in content
    assert r"{\k" not in content


def test_shorts_captions_missing_transcript_raises(isolated_cwd):

    create_project("lesson-001")
    create_clip("lesson-001", "1.1")

    import pytest
    with pytest.raises(FileNotFoundError, match="no transcript"):
        build_shorts_captions("lesson-001", "1.1")
