import typer
from rich.console import Console

from nexasec.core.clip import create_clip
from nexasec.services.clip_importer import import_clip


app = typer.Typer()

console = Console()


@app.command()
def create(
    project: str,
    clip_name: str
):
    """
    Create a new video clip inside a lesson.
    """

    try:

        create_clip(
            project,
            clip_name
        )

        console.print(
            f"[bold green]✔ Clip '{clip_name}' created[/bold green]"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)



@app.command()
def import_video(
    project: str,
    clip_name: str,
    video_path: str
):
    """
    Import a raw video into a clip.
    """

    try:

        output = import_clip(
            project,
            clip_name,
            video_path
        )

        console.print(
            f"[bold green]✔ Imported:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)
