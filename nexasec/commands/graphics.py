import typer
from rich.console import Console

from nexasec.services.motion_graphics import build_lower_third


app = typer.Typer()

console = Console()


@app.command(name="lower-third")
def lower_third(
    project: str,
    clip_name: str,
    name: str,
    title: str,
    accent_color: str = typer.Option(None, "--accent-color"),
    text_color: str = typer.Option(None, "--text-color"),
    background_color: str = typer.Option(None, "--background-color"),
):
    """
    Render a lower-third graphic (name + title card) for a clip,
    using the HyperFrames Motion Graphics Engine. Output is a
    transparent WebM ready to composite over video in the Render
    Engine (M6).
    """

    try:

        output = build_lower_third(
            project,
            clip_name,
            name,
            title,
            accent_color=accent_color,
            text_color=text_color,
            background_color=background_color,
        )

        console.print(
            f"[bold green]✔ Lower-third rendered:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)
