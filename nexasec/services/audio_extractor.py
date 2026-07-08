from pathlib import Path
import subprocess


def extract_audio(
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

    return output
