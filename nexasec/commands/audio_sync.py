import typer
from pathlib import Path
from rich.console import Console

from nexasec.services.audio_sync import sync_audio


app = typer.Typer()

console = Console()


@app.command()
def sync(
    project: str,
):

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

        sync_audio(
            str(video_path),
            str(audio_path),
            str(output_path)
        )

        console.print(
            "[bold green]✔ Audio synced successfully[/bold green]"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)
