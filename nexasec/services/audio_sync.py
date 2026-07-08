from pathlib import Path
import subprocess


def sync_audio(
    video_path: str,
    audio_path: str,
    output_path: str
):

    video = Path(video_path)
    audio = Path(audio_path)
    output = Path(output_path)

    if not video.exists():
        raise FileNotFoundError(video)

    if not audio.exists():
        raise FileNotFoundError(audio)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-y",

        "-i",
        str(video),

        "-i",
        str(audio),

        "-map",
        "0:v:0",

        "-map",
        "1:a:0",

        # Convert ProRes -> H264
        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        # Audio
        "-c:a",
        "aac",

        "-b:a",
        "320k",

        "-ar",
        "48000",

        str(output)
    ]

    subprocess.run(
        command,
        check=True
    )

    return output
