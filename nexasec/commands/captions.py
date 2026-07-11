import typer
from rich.console import Console

from nexasec.services.caption_builder import (
    build_youtube_captions,
    build_shorts_captions,
)


app = typer.Typer()

console = Console()


@app.command()
def youtube(
    project: str
):
    """
    Build clean bottom-of-screen YouTube captions (SRT + ASS) for a
    project, assembled from the timeline.
    """

    try:

        srt_path, ass_path, warnings = build_youtube_captions(project)

        for warning in warnings:
            console.print(
                f"[yellow]⚠ {warning}[/yellow]"
            )

        console.print(
            f"[bold green]✔ YouTube captions built:[/bold green]\n"
            f"  SRT: {srt_path}\n"
            f"  ASS: {ass_path}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command()
def shorts(
    project: str,
    clip_name: str
):
    """
    Build karaoke-style word-by-word captions (ASS) for a single
    clip's Shorts/Reels/TikTok export.
    """

    try:

        output = build_shorts_captions(project, clip_name)

        console.print(
            f"[bold green]✔ Shorts captions built:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)
