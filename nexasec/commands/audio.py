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
    Extract audio from project video.
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
