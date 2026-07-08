from pathlib import Path
import shutil
import json

from nexasec.services.video_analyzer import analyze_video
from nexasec.services.video_parser import parse_video_metadata


def import_clip(
    project: str,
    clip_name: str,
    video_path: str
):

    clip_folder = (
        Path("projects")
        / project
        / "sources"
        / "clips"
        / clip_name
    )

    if not clip_folder.exists():
        raise FileNotFoundError(
            f"Clip '{clip_name}' does not exist. Create it first."
        )


    source = Path(video_path)

    if not source.exists():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )


    video_folder = (
        clip_folder
        / "video"
    )

    video_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    destination = (
        video_folder
        / source.name
    )


    shutil.copy2(
        source,
        destination
    )


    raw_data = analyze_video(
        str(destination)
    )


    metadata = parse_video_metadata(
        raw_data,
        source.name
    )


    metadata_file = (
        clip_folder
        / "metadata.json"
    )


    with open(
        metadata_file,
        "r",
        encoding="utf-8"
    ) as file:

        clip_metadata = json.load(file)


    clip_metadata["video"] = {
        "file": source.name,
        "duration": metadata.duration,
        "resolution": f"{metadata.width}x{metadata.height}",
        "fps": metadata.fps,
        "codec": metadata.video_codec
    }


    clip_metadata["status"] = "imported"


    with open(
        metadata_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            clip_metadata,
            file,
            indent=4,
            ensure_ascii=False
        )


    return destination
