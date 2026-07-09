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
