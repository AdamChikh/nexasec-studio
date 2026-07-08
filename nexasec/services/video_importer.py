from pathlib import Path
import shutil

from nexasec.services.video_analyzer import analyze_video
from nexasec.services.video_parser import parse_video_metadata
from nexasec.core.metadata import update_video_metadata


def import_video(
    project_name: str,
    video_path: str
) -> Path:

    project = Path("projects") / project_name

    if not project.exists():
        raise FileNotFoundError(
            f"Project '{project_name}' does not exist."
        )

    source = Path(video_path)

    if not source.exists():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    destination = (
        project
        / "assets"
        / "video"
        / "originals"
        / "source.mp4"
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
        destination.name
    )

    update_video_metadata(
        project_name,
        metadata.__dict__
    )

    return destination
