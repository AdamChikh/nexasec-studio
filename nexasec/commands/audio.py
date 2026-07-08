import typer
from rich.console import Console
from pathlib import Path

from nexasec.services.audio_extractor import extract_audio
from nexasec.services.audio_sync import sync_audio


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


@app.command()
def sync(
    project: str,
):
    """
    Replace camera audio with microphone audio.
    """

    video_path = (
        Path("projects")
        / project
        / "assets"
        / "video"
        / "originals"
        / "1.1.mov"
    )

    audio_path = (
        Path("projects")
        / project
        / "assets"
        / "audio"
        / "1.1.wav"
    )

    output_path = (
        Path("projects")
        / project
        / "assets"
        / "video"
        / "processed"
        / "master.mp4"
    )

    try:

        output = sync_audio(
            str(video_path),
            str(audio_path),
            str(output_path)
        )

        console.print(
            f"[bold green]✔ Audio synced successfully:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)
