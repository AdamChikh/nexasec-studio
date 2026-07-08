import json
from pathlib import Path


DEFAULT_STYLE = {
    "brand": "NexaSec",

    "colors": {
        "background": "#0A0A0C",
        "gold": "#C6A15B",
        "text": "#FFFFFF"
    },

    "fonts": {
        "title": "Inter",
        "body": "Inter",
        "code": "JetBrains Mono"
    },

    "captions": {
        "youtube": {
            "size": 48,
            "position": "bottom"
        },

        "shorts": {
            "size": 72,
            "position": "center"
        }
    }
}


def create_style(project_path: Path):

    file = project_path / "style.json"

    with open(file, "w", encoding="utf-8") as f:
        json.dump(
            DEFAULT_STYLE,
            f,
            indent=4,
            ensure_ascii=False
        )