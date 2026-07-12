from pathlib import Path

from nexasec.core.clip_store import clip_folder, load_clip, save_clip
from nexasec.services.audio_sync import sync_audio
from nexasec.services.audio_aligner import find_audio_offset
from nexasec.services.video_analyzer import analyze_video
from nexasec.services.video_parser import parse_video_metadata


def sync_clip(project: str, clip_name: str, audio_offset: float | None = None) -> tuple[Path, float]:
    """
    Replace a clip's camera audio with its attached microphone
    audio, producing synced.mp4. Requires both video and audio to
    already be attached.

    Camera and external mic recordings almost never start at exactly
    the same instant -- the mic is very often started before the
    camera, or the two files otherwise drift. If audio_offset isn't
    given explicitly, this auto-detects it via cross-correlation
    (services/audio_aligner.py) between the video's own built-in
    audio track and the external mic recording, then trims the
    external audio to that detected alignment point before syncing.
    If the video has no audio track to use as a reference, falls
    back to offset 0.0 (unable to auto-detect).

    After syncing, re-probes the actual output file rather than
    trusting the pre-sync duration -- sync_audio uses -shortest, so
    the synced file's real duration is min(video, audio) duration,
    which is very often NOT identical to the original video's
    duration.
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

    if audio_offset is None:
        try:
            audio_offset = find_audio_offset(str(video_path), str(audio_path))
        except RuntimeError:
            # video has no audio track to align against -- can't
            # auto-detect, assume they start together
            audio_offset = 0.0

    sync_audio(
        str(video_path),
        str(audio_path),
        str(output_path),
        audio_offset=audio_offset,
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

    return output_path, audio_offset
