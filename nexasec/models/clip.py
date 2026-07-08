from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class ClipVideo:

    file: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None



@dataclass
class ClipAudio:

    file: Optional[str] = None
    type: str = "microphone"
    sample_rate: Optional[int] = None



@dataclass
class ClipLayout:

    youtube: str = "full"
    shorts: str = "crop"



@dataclass
class ClipMetadata:

    name: str

    type: str = "camera"

    role: str = "main"

    status: str = "raw"

    video: ClipVideo = field(
        default_factory=ClipVideo
    )

    audio: ClipAudio = field(
        default_factory=ClipAudio
    )

    layout: ClipLayout = field(
        default_factory=ClipLayout
    )


    def save(self, path):

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                asdict(self),
                file,
                indent=4,
                ensure_ascii=False
            )
