import typer
from rich.console import Console
from pathlib import Path

from nexasec.services.audio_extractor import extract_audio


app = typer.Typer()

console = Console()


@app.command()
def extract(
    project: str,
):
    """
    Extract audio from camera video.
    """

    video_path = (
        Path("projects")
        / project
        / "assets"
        / "video"
        / "originals"
        / "source.mp4"
    )

    output_path = (
        Path("projects")
        / project
        / "assets"
        / "audio"
        / "source.wav"
    )

    try:

        extract_audio(
            project,
            str(video_path),
            str(output_path)
        )

        console.print(
            "[bold green]✔ Audio extracted successfully[/bold green]"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


# NOTE: the old hardcoded `audio sync` command (which only ever worked
# for a clip literally named "1.1") has been removed. Audio syncing is
# now a per-clip operation: `nexasec clip sync <project> <clip>`.
