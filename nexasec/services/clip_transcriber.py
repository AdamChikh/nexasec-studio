from pathlib import Path

from nexasec.core.clip_store import clip_folder, load_clip, save_clip
from nexasec.services.transcriber import transcribe_audio


def transcribe_clip(
    project: str,
    clip_name: str,
    model_size: str = "small"
) -> Path:
    """
    Transcribe a clip's attached microphone audio with WhisperX and
    store the result under the clip's own captions/raw folder.

    Requires audio to already be attached via
    'nexasec clip attach <project> <clip> audio <file>'.
    """

    metadata = load_clip(project, clip_name)

    if not metadata.audio.file:
        raise ValueError(
            f"Clip '{clip_name}' has no audio attached yet. "
            f"Run 'nexasec clip attach {project} {clip_name} audio <file>' first."
        )

    folder = clip_folder(project, clip_name)

    audio_path = folder / "audio" / metadata.audio.file
    output_path = folder / "captions" / "raw" / "transcript.json"

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    transcribe_audio(
        str(audio_path),
        str(output_path),
        model_size=model_size
    )

    metadata.status = "transcribed"
    save_clip(project, clip_name, metadata)

    return output_path


def transcribe_all_clips(
    project: str,
    model_size: str = "small"
) -> dict[str, Path]:
    """
    Transcribe every clip in a project that has audio attached.
    Clips without audio are skipped, not errored -- a project can
    legitimately mix clips still being imported with clips ready
    to transcribe.
    """

    clips_root = (
        Path("projects")
        / project
        / "sources"
        / "clips"
    )

    if not clips_root.exists():
        raise FileNotFoundError(
            f"Project '{project}' has no clips yet."
        )

    results: dict[str, Path] = {}

    for clip_dir in sorted(clips_root.iterdir()):

        if not clip_dir.is_dir():
            continue

        clip_name = clip_dir.name
        metadata = load_clip(project, clip_name)

        if not metadata.audio.file:
            continue

        results[clip_name] = transcribe_clip(
            project,
            clip_name,
            model_size=model_size
        )

    return results
