from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
import json


@dataclass
class ClipRef:
    """
    A single placement of a clip on a layer's timeline.

    `start` is this placement's position on the overall timeline
    (seconds). `duration` defaults to the clip's own full duration
    but can be trimmed independently later without touching the
    clip's own metadata.
    """

    clip: str
    start: float
    duration: float
    in_point: float = 0.0


@dataclass
class VideoLayer:
    """
    One video track. `role` mirrors ClipMetadata.role
    (main / supporting / overlay) and determines stacking order
    when rendering: overlay layers composite on top of
    supporting/main layers.
    """

    name: str
    role: str
    clips: list[ClipRef] = field(default_factory=list)


@dataclass
class AudioLayer:

    name: str
    clips: list[ClipRef] = field(default_factory=list)


@dataclass
class Timeline:

    version: int = 2
    fps: Optional[float] = None

    video_layers: list[VideoLayer] = field(default_factory=list)
    audio_layers: list[AudioLayer] = field(default_factory=list)

    # Populated in later milestones (M4 caption engine, M5 motion
    # graphics, M6 render/effects) -- the slots exist now so the
    # schema doesn't need another breaking version bump later.
    captions: list[dict] = field(default_factory=list)
    graphics: list[dict] = field(default_factory=list)
    effects: list[dict] = field(default_factory=list)

    def save(self, path):

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(asdict(self), file, indent=4, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Timeline":

        def _layer_clips(layer_data: dict) -> list[ClipRef]:
            return [
                ClipRef(
                    clip=c["clip"],
                    start=c["start"],
                    duration=c["duration"],
                    in_point=c.get("in_point", 0.0),
                )
                for c in layer_data.get("clips", [])
            ]

        video_layers = [
            VideoLayer(
                name=layer["name"],
                role=layer["role"],
                clips=_layer_clips(layer),
            )
            for layer in data.get("video_layers", [])
        ]

        audio_layers = [
            AudioLayer(
                name=layer["name"],
                clips=_layer_clips(layer),
            )
            for layer in data.get("audio_layers", [])
        ]

        return cls(
            version=data.get("version", 2),
            fps=data.get("fps"),
            video_layers=video_layers,
            audio_layers=audio_layers,
            captions=data.get("captions", []),
            graphics=data.get("graphics", []),
            effects=data.get("effects", []),
        )

    @classmethod
    def load(cls, path) -> "Timeline":

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Timeline not found: {path}")

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return cls.from_dict(data)
