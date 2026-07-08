from pathlib import Path
import subprocess
import json


def analyze_video(video_path: str) -> dict:
    path = Path(video_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)
