from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
import json


@dataclass
class ClipVideo:
    """
    Metadata for a clip's video stream.

    This shape must match exactly what services/video_parser.py
    produces and what services/clip_attacher.py writes -- width/height
    stay as separate ints (not a combined "WxH" string) so this data
    can be consumed programmatically (e.g. by the timeline/render
    engines later) without re-parsing a string.

    `file` is the raw imported video (camera/screen recording as
    shot, with whatever audio it originally captured -- often a
    camera's built-in mic). `synced_file`, when present, is the
    version produced by 'clip sync' with the dedicated microphone
    audio muxed in -- this is the one the timeline/render engine
    should actually use when it exists.
    """

    file: Optional[str] = None
    synced_file: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    codec: Optional[str] = None


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

    @classmethod
    def from_dict(cls, data: dict) -> "ClipMetadata":
        """
        Reconstruct a ClipMetadata from a raw dict (e.g. loaded from
        JSON). Handles clips written under the old flat schema
        (no type/role/layout, or a null video/audio) by falling back
        to defaults instead of raising.
        """

        video_data = data.get("video") or {}
        audio_data = data.get("audio") or {}
        layout_data = data.get("layout") or {}

        return cls(
            name=data["name"],
            type=data.get("type", "camera"),
            role=data.get("role", "main"),
            status=data.get("status", "raw"),
            video=ClipVideo(
                file=video_data.get("file"),
                synced_file=video_data.get("synced_file"),
                duration=video_data.get("duration"),
                width=video_data.get("width"),
                height=video_data.get("height"),
                fps=video_data.get("fps"),
                codec=video_data.get("codec"),
            ),
            audio=ClipAudio(
                file=audio_data.get("file"),
                type=audio_data.get("type", "microphone"),
                sample_rate=audio_data.get("sample_rate"),
            ),
            layout=ClipLayout(
                youtube=layout_data.get("youtube", "full"),
                shorts=layout_data.get("shorts", "crop"),
            ),
        )

    @classmethod
    def load(cls, path) -> "ClipMetadata":

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Clip metadata not found: {path}"
            )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return cls.from_dict(data)
