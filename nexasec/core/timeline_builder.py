import json
from pathlib import Path


def build_timeline(project: str):

    project_path = Path("projects") / project

    metadata_path = (
        project_path /
        "metadata.json"
    )

    timeline_path = (
        project_path /
        "timeline" /
        "timeline.json"
    )

    metadata = json.loads(
        metadata_path.read_text()
    )

    video = metadata.get("video")
    audio = metadata.get("audio")


    timeline = {
        "version": 1,
        "fps": video.get("fps") if video else None,
        "tracks": {
            "video": [],
            "audio": [],
            "captions": []
        }
    }


    if video:
        timeline["tracks"]["video"].append(
            {
                "id": "video-001",
                "source": video["filename"],
                "start": 0,
                "duration": video["duration"]
            }
        )


    if audio:
        timeline["tracks"]["audio"].append(
            {
                "id": "audio-001",
                "source": audio["filename"],
                "start": 0
            }
        )


    timeline_path.write_text(
        json.dumps(
            timeline,
            indent=4
        )
    )


    return timeline_path
