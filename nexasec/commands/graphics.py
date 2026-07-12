import typer
from rich.console import Console

from nexasec.services.motion_graphics import (
    build_lower_third,
    build_intro,
    build_outro,
    build_chapter_card,
)


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


@app.command()
def intro(
    project: str,
    subtitle: str = "",
    accent_color: str = typer.Option(None, "--accent-color"),
    text_color: str = typer.Option(None, "--text-color"),
    background_color: str = typer.Option(None, "--background-color"),
):
    """
    Render the intro card (opaque, standalone timeline segment).
    """

    try:

        output = build_intro(
            project,
            subtitle=subtitle,
            accent_color=accent_color,
            text_color=text_color,
            background_color=background_color,
        )

        console.print(
            f"[bold green]✔ Intro rendered:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command()
def outro(
    project: str,
    cta_text: str = "Subscribe for more",
    accent_color: str = typer.Option(None, "--accent-color"),
    text_color: str = typer.Option(None, "--text-color"),
    background_color: str = typer.Option(None, "--background-color"),
):
    """
    Render the outro card (opaque, standalone timeline segment).
    """

    try:

        output = build_outro(
            project,
            cta_text=cta_text,
            accent_color=accent_color,
            text_color=text_color,
            background_color=background_color,
        )

        console.print(
            f"[bold green]✔ Outro rendered:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command(name="chapter-card")
def chapter_card(
    project: str,
    chapter_id: str,
    chapter_title: str,
    chapter_number: str = typer.Option(None, "--chapter-number"),
    accent_color: str = typer.Option(None, "--accent-color"),
    text_color: str = typer.Option(None, "--text-color"),
    background_color: str = typer.Option(None, "--background-color"),
):
    """
    Render a chapter card overlay (brief, announces a new section).
    """

    try:

        output = build_chapter_card(
            project,
            chapter_id,
            chapter_title,
            chapter_number=chapter_number,
            accent_color=accent_color,
            text_color=text_color,
            background_color=background_color,
        )

        console.print(
            f"[bold green]✔ Chapter card rendered:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)
