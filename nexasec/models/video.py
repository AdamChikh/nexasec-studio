from dataclasses import dataclass


@dataclass
class VideoMetadata:
    filename: str
    duration: float
    width: int
    height: int
    fps: float
    video_codec: str
    audio_codec: str | None = None
