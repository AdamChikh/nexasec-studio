from pathlib import Path

from nexasec.models.clip import ClipMetadata


def clip_folder(project: str, clip_name: str) -> Path:
    return (
        Path("projects")
        / project
        / "sources"
        / "clips"
        / clip_name
    )


def clip_metadata_path(project: str, clip_name: str) -> Path:
    return clip_folder(project, clip_name) / "metadata.json"


def clip_exists(project: str, clip_name: str) -> bool:
    return clip_metadata_path(project, clip_name).exists()


def load_clip(project: str, clip_name: str) -> ClipMetadata:

    path = clip_metadata_path(project, clip_name)

    if not path.exists():
        raise FileNotFoundError(
            f"Clip '{clip_name}' does not exist in project "
            f"'{project}'. Create it first with "
            f"'nexasec clip create {project} {clip_name}'."
        )

    return ClipMetadata.load(path)


def save_clip(project: str, clip_name: str, metadata: ClipMetadata) -> Path:

    path = clip_metadata_path(project, clip_name)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    metadata.save(path)

    return path


def clip_video_path(project: str, clip_name: str) -> Path:
    """
    Resolve the correct video file to actually use for this clip:
    the audio-synced version if 'clip sync' has been run, otherwise
    the raw imported video. Consumers (timeline validation, render
    engine) should always go through this rather than reading
    metadata.video.file directly, so a synced clip's dedicated
    microphone audio actually gets used downstream.
    """

    metadata = load_clip(project, clip_name)

    filename = metadata.video.synced_file or metadata.video.file

    if not filename:
        raise ValueError(
            f"Clip '{clip_name}' has no video attached yet."
        )

    return clip_folder(project, clip_name) / "video" / filename
