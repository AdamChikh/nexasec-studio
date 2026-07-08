from pathlib import Path
import json


def create_project(name: str) -> None:
    root = Path("projects") / name

    folders = [
        "assets/video",
        "assets/audio",
        "assets/images",
        "assets/broll",
        "captions",
        "timeline",
        "renders",
        "exports",
    ]

    for folder in folders:
        (root / folder).mkdir(parents=True, exist_ok=True)

    (root / "script.md").touch()
    (root / "notes.md").touch()

    metadata = {
        "title": "",
        "status": "draft",
        "language": "ar-DZ",
        "version": 1,
    }

    with open(root / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)