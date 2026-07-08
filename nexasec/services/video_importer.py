from pathlib import Path
import shutil


def import_video(project_name: str, video_path: str) -> None:
    project = Path("projects") / project_name

    if not project.exists():
        raise FileNotFoundError(f"Project '{project_name}' does not exist.")

    source = Path(video_path)

    if not source.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    destination = project / "assets" / "video" / "source.mp4"

    shutil.copy2(source, destination)
