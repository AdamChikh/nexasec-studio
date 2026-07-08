from pathlib import Path
import subprocess

from nexasec.core.metadata import update_audio_metadata


def extract_audio(
    project_name: str,
    video_path: str,
    output_path: str
) -> Path:

    video = Path(video_path)
    output = Path(output_path)

    if not video.exists():
        raise FileNotFoundError(
            f"Video not found: {video}"
        )

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-i",
        str(video),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(output),
        "-y"
    ]

    subprocess.run(
        command,
        check=True
    )

    update_audio_metadata(
        project_name,
        {
            "filename": output.name,
            "format": "wav",
            "sample_rate": 16000,
            "channels": 1
        }
    )

    return output