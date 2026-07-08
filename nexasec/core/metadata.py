from pathlib import Path
import json


def load_metadata(project_name: str) -> dict:
    path = (
        Path("projects")
        / project_name
        / "metadata.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            "metadata.json not found"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_metadata(
    project_name: str,
    metadata: dict
) -> None:

    path = (
        Path("projects")
        / project_name
        / "metadata.json"
    )

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
) -> None:

    metadata = load_metadata(project_name)

    metadata["video"] = video_data

    save_metadata(
        project_name,
        metadata
    )
