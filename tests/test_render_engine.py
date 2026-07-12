from pathlib import Path
import subprocess

import pytest

from nexasec.core.clip import create_clip
from nexasec.core.clip_store import load_clip, save_clip
from nexasec.core.project import create_project
from nexasec.core.timeline import build_timeline
from nexasec.services.clip_attacher import attach_video
from nexasec.services.render_engine import (
    render_youtube,
    render_shorts,
    _has_audio_stream,
)
from nexasec.services.video_analyzer import analyze_video
from nexasec.services.video_parser import parse_video_metadata


def _probe(path: Path):
    raw = analyze_video(str(path))
    return parse_video_metadata(raw, path.name)


def _make_video_only_clip(path: Path, duration: float = 2.0):
    """
    Generate a real video-only file (no audio stream at all) via
    ffmpeg's testsrc, matching what HyperFrames' intro/outro output
    actually looks like (video-only mp4).
    """

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"testsrc=duration={duration}:size=640x360:rate=30",
            "-c:v", "libx264", "-preset", "ultrafast",
            str(path),
        ],
        check=True,
        capture_output=True,
    )


def _setup_project_with_clips(project, test_video):
    """
    Create a project with two short imported clips ready for
    timeline building.
    """

    create_project(project)

    create_clip(project, "1.1")
    attach_video(project, "1.1", str(test_video))

    create_clip(project, "2.1")
    attach_video(project, "2.1", str(test_video))

    build_timeline(project)


def test_render_youtube_produces_correct_resolution(isolated_cwd, test_video):

    _setup_project_with_clips("lesson-001", test_video)

    output = render_youtube("lesson-001", include_intro=False, include_outro=False, burn_captions=False)

    assert output.exists()

    metadata = _probe(output)
    assert metadata.width == 1920
    assert metadata.height == 1080


def test_render_youtube_duration_matches_sum_of_clips(isolated_cwd, test_video):

    _setup_project_with_clips("lesson-001", test_video)

    output = render_youtube("lesson-001", include_intro=False, include_outro=False, burn_captions=False)

    metadata = _probe(output)

    # two 5s clips concatenated -> ~10s (allow encoding rounding)
    assert 9.0 < metadata.duration < 11.0


def test_render_youtube_includes_intro_and_outro(isolated_cwd, test_video):

    _setup_project_with_clips("lesson-001", test_video)

    graphics_dir = Path("projects/lesson-001/assets/graphics")
    graphics_dir.mkdir(parents=True, exist_ok=True)
    _make_video_only_clip(graphics_dir / "intro.mp4", duration=1.0)
    _make_video_only_clip(graphics_dir / "outro.mp4", duration=1.0)

    output = render_youtube("lesson-001", burn_captions=False)

    metadata = _probe(output)

    # 1s intro + 5s + 5s + 1s outro = 12s
    assert 11.0 < metadata.duration < 13.0


def test_render_youtube_handles_video_only_clips_mixed_with_audio_clips(isolated_cwd, test_video):
    """
    The riskiest part of the design: silent-audio injection for
    clips with no audio stream (like HyperFrames intro/outro), mixed
    with clips that DO have real audio, in the same concat. Must not
    crash and must produce a file with a valid audio stream overall.
    """

    _setup_project_with_clips("lesson-001", test_video)  # has audio

    graphics_dir = Path("projects/lesson-001/assets/graphics")
    graphics_dir.mkdir(parents=True, exist_ok=True)
    _make_video_only_clip(graphics_dir / "intro.mp4", duration=1.0)  # no audio

    output = render_youtube("lesson-001", include_outro=False, burn_captions=False)

    assert output.exists()
    assert _has_audio_stream(output)


def test_render_youtube_burns_in_captions(isolated_cwd, test_video):

    _setup_project_with_clips("lesson-001", test_video)

    captions_dir = Path("projects/lesson-001/captions/youtube")
    captions_dir.mkdir(parents=True, exist_ok=True)
    (captions_dir / "captions.ass").write_text(
        "[Script Info]\nPlayResX: 1920\nPlayResY: 1080\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, "
        "SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, "
        "MarginV, Encoding\n"
        "Style: Default,Inter,48,&H00FFFFFF,&H00C6A15B,&H00000000,"
        "&H64000000,0,0,0,0,100,100,0,0,1,2,0,2,40,40,60,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, "
        "MarginR, MarginV, Effect, Text\n"
        "Dialogue: 0,0:00:00.00,0:00:03.00,Default,,0,0,0,,test caption\n",
        encoding="utf-8",
    )

    # should not raise -- proves libass is actually linked and the
    # subtitles filter + our generated ASS file both work for real
    output = render_youtube("lesson-001", include_intro=False, include_outro=False)

    assert output.exists()


def test_render_youtube_no_timeline_raises(isolated_cwd):

    create_project("lesson-001")

    with pytest.raises(ValueError, match="no timeline yet"):
        render_youtube("lesson-001")


def test_render_youtube_empty_timeline_raises(isolated_cwd):

    from nexasec.core.timeline import create_timeline

    create_project("lesson-001")
    create_timeline("lesson-001")

    with pytest.raises(ValueError, match="no clips on its timeline"):
        render_youtube("lesson-001")


def test_render_shorts_produces_correct_resolution(isolated_cwd, test_video):

    create_project("lesson-001")
    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))

    output = render_shorts("lesson-001", "1.1", burn_captions=False)

    assert output.exists()

    metadata = _probe(output)
    assert metadata.width == 1080
    assert metadata.height == 1920


def test_render_shorts_preserves_audio(isolated_cwd, test_video):

    create_project("lesson-001")
    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))

    output = render_shorts("lesson-001", "1.1", burn_captions=False)

    assert _has_audio_stream(output)


def test_render_shorts_burns_in_karaoke_captions(isolated_cwd, test_video):

    create_project("lesson-001")
    create_clip("lesson-001", "1.1")
    attach_video("lesson-001", "1.1", str(test_video))

    captions_dir = Path("projects/lesson-001/sources/clips/1.1/captions/rendered")
    captions_dir.mkdir(parents=True, exist_ok=True)
    (captions_dir / "shorts.ass").write_text(
        "[Script Info]\nPlayResX: 1080\nPlayResY: 1920\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, "
        "SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, "
        "MarginV, Encoding\n"
        "Style: Default,Inter,72,&H00FFFFFF,&H00C6A15B,&H00000000,"
        "&H64000000,0,0,0,0,100,100,0,0,1,2,0,5,40,40,250,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, "
        "MarginR, MarginV, Effect, Text\n"
        "Dialogue: 0,0:00:00.00,0:00:02.00,Default,,0,0,0,,"
        r"{\k50}hello {\k50}world" "\n",
        encoding="utf-8",
    )

    output = render_shorts("lesson-001", "1.1")

    assert output.exists()
