from pathlib import Path
import subprocess


def sync_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    audio_offset: float = 0.0,
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

        # -ss before this -i trims the external audio to start at
        # its detected alignment point (see services/audio_aligner.py)
        # rather than assuming video and audio started recording at
        # exactly the same instant, which is very often not true for
        # two separately-started recording devices.
        "-ss",
        str(audio_offset),

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

        "-shortest",

        str(output)
    ]

    subprocess.run(
        command,
        check=True
    )

    return output
