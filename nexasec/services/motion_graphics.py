from pathlib import Path
import json
import os
import shutil
import subprocess


HYPERFRAMES_PROJECT_DIR = Path("motion-graphics")

RENDER_TIMEOUT_SECONDS = 300


def check_hyperframes_available() -> None:
    """
    Raise a clear error if Node.js/npx isn't available, rather than
    letting subprocess fail with an opaque "command not found".
    HyperFrames requires Node.js 22+.
    """

    if shutil.which("node") is None:
        raise RuntimeError(
            "Node.js is not installed or not on PATH. HyperFrames "
            "(the Motion Graphics Engine) requires Node.js 22+. "
            "Install it, then verify with 'node --version'."
        )

    if shutil.which("npx") is None:
        raise RuntimeError(
            "npx is not available (it ships with Node.js/npm). "
            "Verify your Node.js installation with 'npx --version'."
        )


def render_composition(
    composition_name: str,
    variables: dict,
    output_path: Path,
    output_format: str = "webm",
) -> Path:
    """
    Render a HyperFrames composition to a file, e.g. a transparent
    WebM overlay for later compositing by the Render Engine (M6).

    composition_name is the filename (without .html) under
    motion-graphics/compositions/.
    """

    check_hyperframes_available()

    composition_path = (
        HYPERFRAMES_PROJECT_DIR / "compositions" / f"{composition_name}.html"
    )

    if not composition_path.exists():
        raise FileNotFoundError(
            f"No such composition template: {composition_path}"
        )

    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "npx",
        "--yes",
        "hyperframes",
        "render",
        "--composition",
        str(Path("compositions") / f"{composition_name}.html"),
        "--variables",
        json.dumps(variables),
        "--format",
        output_format,
        "--output",
        str(output_path),
        "--strict-variables",
    ]

    env = os.environ.copy()
    env["HYPERFRAMES_NO_TELEMETRY"] = "1"
    env["HYPERFRAMES_NO_UPDATE_CHECK"] = "1"

    result = subprocess.run(
        command,
        cwd=str(HYPERFRAMES_PROJECT_DIR),
        capture_output=True,
        text=True,
        timeout=RENDER_TIMEOUT_SECONDS,
        stdin=subprocess.DEVNULL,
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"HyperFrames render failed for '{composition_name}' "
            f"(exit code {result.returncode}):\n"
            f"--- stdout ---\n{result.stdout}\n"
            f"--- stderr ---\n{result.stderr}"
        )

    if not output_path.exists():
        raise RuntimeError(
            f"HyperFrames reported success but no output file was "
            f"produced at {output_path}. stdout:\n{result.stdout}"
        )

    return output_path


def build_lower_third(
    project: str,
    clip_name: str,
    name: str,
    title: str,
    accent_color: str | None = None,
    text_color: str | None = None,
    background_color: str | None = None,
) -> Path:
    """
    Render a lower-third graphic (name + title card) for a clip,
    using NexaSec's Obsidian & Gold defaults unless overridden.
    """

    variables = {"name": name, "title": title}
    _add_color_overrides(variables, accent_color, text_color, background_color)

    output_path = (
        Path("projects")
        / project
        / "assets"
        / "graphics"
        / "lower-thirds"
        / f"{clip_name}.webm"
    )

    return render_composition(
        "lower-third",
        variables,
        output_path,
        output_format="webm",
    )


def build_chapter_card(
    project: str,
    chapter_id: str,
    chapter_title: str,
    chapter_number: str | None = None,
    accent_color: str | None = None,
    text_color: str | None = None,
    background_color: str | None = None,
) -> Path:
    """
    Render a chapter card overlay (brief, announces a new section).
    """

    variables = {"chapterTitle": chapter_title}

    if chapter_number is not None:
        variables["chapterNumber"] = chapter_number

    _add_color_overrides(variables, accent_color, text_color, background_color)

    output_path = (
        Path("projects")
        / project
        / "assets"
        / "graphics"
        / "chapter-cards"
        / f"{chapter_id}.webm"
    )

    return render_composition(
        "chapter-card",
        variables,
        output_path,
        output_format="webm",
    )


def build_intro(
    project: str,
    subtitle: str = "",
    accent_color: str | None = None,
    text_color: str | None = None,
    background_color: str | None = None,
) -> Path:
    """
    Render the intro card. Opaque (not a transparent overlay) --
    intros are standalone timeline segments spliced in, not
    composited over existing footage.
    """

    variables = {"subtitle": subtitle}
    _add_color_overrides(variables, accent_color, text_color, background_color)

    output_path = (
        Path("projects") / project / "assets" / "graphics" / "intro.mp4"
    )

    return render_composition(
        "intro",
        variables,
        output_path,
        output_format="mp4",
    )


def build_outro(
    project: str,
    cta_text: str = "Subscribe for more",
    accent_color: str | None = None,
    text_color: str | None = None,
    background_color: str | None = None,
) -> Path:
    """
    Render the outro card. Opaque, same reasoning as build_intro.
    """

    variables = {"ctaText": cta_text}
    _add_color_overrides(variables, accent_color, text_color, background_color)

    output_path = (
        Path("projects") / project / "assets" / "graphics" / "outro.mp4"
    )

    return render_composition(
        "outro",
        variables,
        output_path,
        output_format="mp4",
    )


def _add_color_overrides(
    variables: dict,
    accent_color: str | None,
    text_color: str | None,
    background_color: str | None,
) -> None:

    if accent_color is not None:
        variables["accentColor"] = accent_color

    if text_color is not None:
        variables["textColor"] = text_color

    if background_color is not None:
        variables["backgroundColor"] = background_color
