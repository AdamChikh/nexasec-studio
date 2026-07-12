from pathlib import Path

from nexasec.core.clip_store import clip_folder, load_clip, save_clip
from nexasec.services.audio_sync import sync_audio
from nexasec.services.video_analyzer import analyze_video
from nexasec.services.video_parser import parse_video_metadata


def sync_clip(project: str, clip_name: str) -> Path:
    """
    Replace a clip's camera audio with its attached microphone
    audio, producing synced.mp4. Requires both video and audio to
    already be attached.

    After syncing, re-probes the actual output file rather than
    trusting the pre-sync duration -- sync_audio uses -shortest, so
    the synced file's real duration is min(video, audio) duration,
    which is very often NOT identical to the original video's
    duration (camera and mic are separate recordings that rarely
    start/stop at exactly the same instant).
    """

    metadata = load_clip(project, clip_name)

    if not metadata.video.file:
        raise ValueError(
            f"Clip '{clip_name}' has no video attached yet. "
            f"Run 'nexasec clip attach {project} {clip_name} video <file>' first."
        )

    if not metadata.audio.file:
        raise ValueError(
            f"Clip '{clip_name}' has no audio attached yet. "
            f"Run 'nexasec clip attach {project} {clip_name} audio <file>' first."
        )

    folder = clip_folder(project, clip_name)

    video_path = folder / "video" / metadata.video.file
    audio_path = folder / "audio" / metadata.audio.file
    output_path = folder / "video" / "synced.mp4"

    sync_audio(
        str(video_path),
        str(audio_path),
        str(output_path),
    )

    raw_data = analyze_video(str(output_path))
    parsed = parse_video_metadata(raw_data, output_path.name)

    metadata.video.synced_file = output_path.name
    metadata.video.duration = parsed.duration
    metadata.video.width = parsed.width
    metadata.video.height = parsed.height
    metadata.video.fps = parsed.fps
    metadata.video.codec = parsed.video_codec

    metadata.status = "synced"
    save_clip(project, clip_name, metadata)

    return output_path
