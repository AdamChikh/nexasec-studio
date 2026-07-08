from pathlib import Path
import json

from nexasec.core.style import create_style


def create_project(name: str) -> None:

    root = Path("projects") / name

    folders = [
        "assets/broll",
        "assets/images",

        "assets/music",
        "assets/sfx",

        "assets/graphics/logos",
        "assets/graphics/lower-thirds",
        "assets/graphics/overlays",

        "assets/fonts",

        "sources/clips",

        "captions",
        "timelines",

        "renders",
        "exports/youtube",
        "exports/shorts",
    ]

    for folder in folders:
        (root / folder).mkdir(
            parents=True,
            exist_ok=True
        )

    (root / "script.md").touch()
    (root / "notes.md").touch()

    metadata = {
        "title": "",
        "status": "draft",
        "language": "ar-DZ",
        "version": 1,
        "video": None
    }

    with open(
        root / "metadata.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False
        )

    create_style(root)