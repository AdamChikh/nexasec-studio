from pathlib import Path
import shutil

from nexasec.core.clip_store import (
    clip_folder,
    load_clip,
    save_clip,
)
from nexasec.models.clip import ClipVideo, ClipAudio
from nexasec.services.video_analyzer import analyze_video
from nexasec.services.video_parser import parse_video_metadata


SUPPORTED_MEDIA_TYPES = ("video", "audio")


def _copy_into(
    clip_name: str,
    project: str,
    subfolder: str,
    source_path: str
) -> Path:

    source = Path(source_path)

    if not source.exists():
        raise FileNotFoundError(
            f"File not found: {source_path}"
        )

    destination_folder = (
        clip_folder(project, clip_name) / subfolder
    )

    destination_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = destination_folder / source.name

    shutil.copy2(source, destination)

    return destination


def attach_video(
    project: str,
    clip_name: str,
    source_path: str
) -> Path:
    """
    Attach a video file to a clip: copy it in, analyze it with
    ffprobe, and update the clip's ClipVideo metadata.
    """

    metadata = load_clip(project, clip_name)

    destination = _copy_into(
        clip_name,
        project,
        "video",
        source_path
    )

    raw_data = analyze_video(str(destination))

    parsed = parse_video_metadata(raw_data, destination.name)

    metadata.video = ClipVideo(
        file=parsed.filename,
        duration=parsed.duration,
        width=parsed.width,
        height=parsed.height,
        fps=parsed.fps,
        codec=parsed.video_codec,
    )

    metadata.status = "imported"

    save_clip(project, clip_name, metadata)

    return destination


def attach_audio(
    project: str,
    clip_name: str,
    source_path: str,
    audio_type: str = "microphone"
) -> Path:
    """
    Attach an audio file to a clip (e.g. dedicated microphone
    recording matching the clip's camera video).
    """

    metadata = load_clip(project, clip_name)

    destination = _copy_into(
        clip_name,
        project,
        "audio",
        source_path
    )

    metadata.audio = ClipAudio(
        file=destination.name,
        type=audio_type,
        sample_rate=metadata.audio.sample_rate,
    )

    save_clip(project, clip_name, metadata)

    return destination


def attach(
    project: str,
    clip_name: str,
    media_type: str,
    source_path: str
) -> Path:
    """
    Dispatch to the right attach_* function by media type.
    """

    if media_type == "video":
        return attach_video(project, clip_name, source_path)

    if media_type == "audio":
        return attach_audio(project, clip_name, source_path)

    raise ValueError(
        f"Unsupported media type '{media_type}'. "
        f"Supported types: {', '.join(SUPPORTED_MEDIA_TYPES)}"
    )
