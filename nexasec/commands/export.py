import typer
from rich.console import Console

from nexasec.services.render_engine import render_youtube, render_shorts


app = typer.Typer()

console = Console()


@app.command()
def youtube(
    project: str,
    include_intro: bool = True,
    include_outro: bool = True,
    burn_captions: bool = True,
):
    """
    Render the full 16:9 YouTube export from the project's timeline.
    """

    try:

        output = render_youtube(
            project,
            include_intro=include_intro,
            include_outro=include_outro,
            burn_captions=burn_captions,
        )

        console.print(
            f"[bold green]✔ YouTube export rendered:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command()
def shorts(
    project: str,
    clip_name: str,
    burn_captions: bool = True,
):
    """
    Render a single clip as a 9:16 Shorts/Reels/TikTok export.
    """

    try:

        output = render_shorts(
            project,
            clip_name,
            burn_captions=burn_captions,
        )

        console.print(
            f"[bold green]✔ Shorts export rendered:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)
