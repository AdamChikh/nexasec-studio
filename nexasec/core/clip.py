from pathlib import Path

from nexasec.models.clip import ClipMetadata


def create_clip(
    project: str,
    clip_name: str
):

    clip_path = (
        Path("projects")
        / project
        / "sources"
        / "clips"
        / clip_name
    )


    folders = [
        "video",
        "audio",
        "captions",
    ]


    for folder in folders:

        (
            clip_path / folder
        ).mkdir(
            parents=True,
            exist_ok=True
        )


    metadata = ClipMetadata(
        name=clip_name
    )


    metadata.save(
        clip_path / "metadata.json"
    )


    return clip_path
