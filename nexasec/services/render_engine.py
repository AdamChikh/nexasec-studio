from pathlib import Path
import subprocess

from nexasec.core.clip_store import clip_folder, clip_video_path
from nexasec.core.timeline import Timeline, timeline_path
from nexasec.services.video_analyzer import analyze_video
from nexasec.services.video_parser import parse_video_metadata


YOUTUBE_WIDTH, YOUTUBE_HEIGHT = 1920, 1080
SHORTS_WIDTH, SHORTS_HEIGHT = 1080, 1920
TARGET_FPS = 30
SAMPLE_RATE = 48000

RENDER_TIMEOUT_SECONDS = 1800


def _has_audio_stream(path: Path) -> bool:
    raw = analyze_video(str(path))
    return any(s["codec_type"] == "audio" for s in raw["streams"])


def _probe_duration(path: Path) -> float:
    raw = analyze_video(str(path))
    parsed = parse_video_metadata(raw, path.name)
    return parsed.duration


def _escape_subtitles_path(path: Path) -> str:
    """
    ffmpeg's subtitles filter uses ':' as an option separator inside
    the filter graph string, so any colon in the path must be
    escaped. Not expected on ordinary Linux/WSL paths, but escaping
    defensively costs nothing.
    """

    escaped = str(path.resolve()).replace("\\", "/")
    escaped = escaped.replace(":", "\\:")
    return escaped


def _run_ffmpeg(command: list[str]) -> None:

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=RENDER_TIMEOUT_SECONDS,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg render failed (exit code {result.returncode}):\n"
            f"{result.stderr}"
        )


def _build_concat_command(
    clip_paths: list[Path],
    output_path: Path,
    width: int,
    height: int,
    fps: int = TARGET_FPS,
    subtitles_path: Path | None = None,
) -> list[str]:
    """
    Build an ffmpeg command that normalizes every clip to identical
    resolution/fps/audio format (regardless of source differences)
    and concatenates them via filter_complex, optionally burning in
    ASS captions on the result.

    Clips with no audio stream (e.g. HyperFrames-rendered intro/outro,
    which are video-only) get a generated silent track matching their
    duration, so the concat filter always has a consistent number of
    audio inputs to work with.
    """

    n = len(clip_paths)

    has_audio = [_has_audio_stream(p) for p in clip_paths]
    durations = [_probe_duration(p) for p in clip_paths]

    input_args: list[str] = []
    for path in clip_paths:
        input_args += ["-i", str(path)]

    silent_input_index: dict[int, int] = {}
    for i, (has_a, duration) in enumerate(zip(has_audio, durations)):
        if not has_a:
            silent_input_index[i] = n + len(silent_input_index)
            input_args += [
                "-f", "lavfi",
                "-t", str(duration),
                "-i", f"anullsrc=channel_layout=stereo:sample_rate={SAMPLE_RATE}",
            ]

    filter_lines: list[str] = []
    concat_inputs: list[str] = []

    for i in range(n):

        v_label = f"v{i}"
        a_label = f"a{i}"

        filter_lines.append(
            f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[{v_label}]"
        )

        audio_source = i if has_audio[i] else silent_input_index[i]

        filter_lines.append(
            f"[{audio_source}:a]aformat=sample_rates={SAMPLE_RATE}:"
            f"channel_layouts=stereo[{a_label}]"
        )

        concat_inputs.append(f"[{v_label}][{a_label}]")

    filter_lines.append(
        "".join(concat_inputs) + f"concat=n={n}:v=1:a=1[concatv][concata]"
    )

    final_video_label = "concatv"

    if subtitles_path is not None:
        escaped = _escape_subtitles_path(subtitles_path)
        filter_lines.append(f"[concatv]subtitles='{escaped}'[outv]")
        final_video_label = "outv"

    filter_complex = ";".join(filter_lines)

    return [
        "ffmpeg", "-y",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", f"[{final_video_label}]",
        "-map", "[concata]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "320k", "-ar", str(SAMPLE_RATE),
        str(output_path),
    ]


def _build_shorts_command(
    clip_path: Path,
    output_path: Path,
    subtitles_path: Path | None = None,
) -> list[str]:
    """
    Convert a single 16:9 clip to 9:16 using a blurred, cropped
    full-bleed background with the original framing preserved and
    centered on top -- the standard technique for reformatting
    horizontal footage to vertical without a naive, content-losing
    center crop.
    """

    filter_lines = [
        f"[0:v]scale={SHORTS_WIDTH}:{SHORTS_HEIGHT}:"
        f"force_original_aspect_ratio=increase,"
        f"crop={SHORTS_WIDTH}:{SHORTS_HEIGHT},gblur=sigma=25,setsar=1[bg]",

        f"[0:v]scale={SHORTS_WIDTH}:-2:"
        f"force_original_aspect_ratio=decrease,setsar=1[fg]",

        "[bg][fg]overlay=(W-w)/2:(H-h)/2[composited]",
    ]

    final_label = "composited"

    if subtitles_path is not None:
        escaped = _escape_subtitles_path(subtitles_path)
        filter_lines.append(f"[composited]subtitles='{escaped}'[outv]")
        final_label = "outv"

    filter_complex = ";".join(filter_lines)

    has_audio = _has_audio_stream(clip_path)

    command = ["ffmpeg", "-y", "-i", str(clip_path)]

    command += ["-filter_complex", filter_complex, "-map", f"[{final_label}]"]

    if has_audio:
        command += [
            "-map", "0:a",
            "-c:a", "aac", "-b:a", "320k", "-ar", str(SAMPLE_RATE),
        ]

    command += [
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        str(output_path),
    ]

    return command


def render_youtube(
    project: str,
    include_intro: bool = True,
    include_outro: bool = True,
    burn_captions: bool = True,
) -> Path:
    """
    Render the full 16:9 YouTube export from the project's timeline.

    NOTE (known limitation, carried from M3): video layers don't
    actually overlap in time today -- clips are placed sequentially
    even across layers -- so there's nothing to composite as
    picture-in-picture yet. Every clip on the timeline becomes its
    own sequential segment in chronological (start-time) order. True
    overlay compositing (e.g. a facecam bubble over concurrent screen
    recording) needs the future clip-pairing feature noted in M3.

    Also NOTE: burned-in caption text uses whatever fonts the ASS
    file's Style block names (e.g. "Inter") via the system's
    fontconfig/libass. If that font isn't actually installed on the
    machine doing the render, libass silently substitutes a default
    font rather than erroring -- not currently guaranteed to look
    correct, just functional.
    """

    try:
        timeline = Timeline.load(timeline_path(project))
    except FileNotFoundError:
        raise ValueError(
            f"Project '{project}' has no timeline yet. Run "
            f"'nexasec timeline build {project}' first."
        )

    all_refs = [
        (clip_ref.clip, clip_ref.start)
        for layer in timeline.video_layers
        for clip_ref in layer.clips
    ]
    all_refs.sort(key=lambda pair: pair[1])

    if not all_refs:
        raise ValueError(
            f"Project '{project}' has no clips on its timeline yet. "
            f"Run 'nexasec timeline build {project}' first."
        )

    clip_paths = [clip_video_path(project, name) for name, _ in all_refs]

    graphics_dir = Path("projects") / project / "assets" / "graphics"
    intro_path = graphics_dir / "intro.mp4"
    outro_path = graphics_dir / "outro.mp4"

    if include_intro and intro_path.exists():
        clip_paths = [intro_path] + clip_paths

    if include_outro and outro_path.exists():
        clip_paths = clip_paths + [outro_path]

    subtitles_path = None

    if burn_captions:
        candidate = (
            Path("projects") / project / "captions" / "youtube" / "captions.ass"
        )
        if candidate.exists():
            subtitles_path = candidate

    output_path = Path("projects") / project / "exports" / "youtube.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = _build_concat_command(
        clip_paths,
        output_path,
        YOUTUBE_WIDTH,
        YOUTUBE_HEIGHT,
        subtitles_path=subtitles_path,
    )

    _run_ffmpeg(command)

    return output_path


def render_shorts(
    project: str,
    clip_name: str,
    burn_captions: bool = True,
) -> Path:
    """
    Render a single clip as a 9:16 Shorts/Reels/TikTok export, per
    the brand brief's "one bite-sized idea per clip" -- Shorts are
    built per-clip, not assembled from the full timeline.
    """

    clip_path = clip_video_path(project, clip_name)

    subtitles_path = None

    if burn_captions:
        candidate = (
            clip_folder(project, clip_name)
            / "captions" / "rendered" / "shorts.ass"
        )
        if candidate.exists():
            subtitles_path = candidate

    output_path = (
        Path("projects") / project / "exports" / "shorts" / f"{clip_name}.mp4"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = _build_shorts_command(
        clip_path,
        output_path,
        subtitles_path=subtitles_path,
    )

    _run_ffmpeg(command)

    return output_path
