import json
from pathlib import Path


def create_timeline(project: str):
    """
    Create empty editing timeline.
    """

    timeline_path = (
        Path("projects")
        / project
        / "timeline"
        / "timeline.json"
    )

    timeline_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    timeline = {
        "version": 1,
        "fps": None,
        "tracks": {
            "video": [],
            "audio": [],
            "captions": []
        }
    }

    timeline_path.write_text(
        json.dumps(
            timeline,
            indent=4
        )
    )

    return timeline_path
