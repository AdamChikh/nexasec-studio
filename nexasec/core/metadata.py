from pathlib import Path
import json


def metadata_path(project_name: str) -> Path:
    return (
        Path("projects")
        / project_name
        / "metadata.json"
    )


def load_metadata(project_name: str) -> dict:

    path = metadata_path(project_name)

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_metadata(
    project_name: str,
    metadata: dict
):

    path = metadata_path(project_name)

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False
        )


def update_video_metadata(
    project_name: str,
    video_data: dict
):

    metadata = load_metadata(project_name)

    metadata["video"] = video_data

    save_metadata(
        project_name,
        metadata
    )


def update_audio_metadata(
    project_name: str,
    audio_data: dict
):

    metadata = load_metadata(project_name)

    metadata["audio"] = audio_data

    save_metadata(
        project_name,
        metadata
    )
