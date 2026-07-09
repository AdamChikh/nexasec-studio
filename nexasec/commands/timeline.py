import typer
from rich.console import Console

from nexasec.core.timeline import (
    create_timeline,
    build_timeline,
    validate_timeline,
)


app = typer.Typer()

console = Console()


@app.command()
def init(
    project: str
):
    """
    Create an empty timeline for a project.
    """

    try:

        path = create_timeline(project)

        console.print(
            f"[bold green]✔ Timeline created:[/bold green] {path}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command()
def build(
    project: str
):
    """
    Build the timeline from every imported clip in the project,
    placing each clip on the video layer implied by its type/role
    (e.g. screen recordings on a base layer, facecam clips on an
    overlay layer).
    """

    try:

        path, warnings = build_timeline(project)

        for warning in warnings:
            console.print(
                f"[yellow]⚠ {warning}[/yellow]"
            )

        console.print(
            f"[bold green]✔ Timeline built:[/bold green] {path}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command()
def validate(
    project: str
):
    """
    Check that every clip referenced in the timeline still exists
    and has video attached.
    """

    try:

        errors = validate_timeline(project)

        if not errors:
            console.print(
                "[bold green]✔ Timeline is valid[/bold green]"
            )
            return

        for error in errors:
            console.print(
                f"[bold red]✖ {error}[/bold red]"
            )

        raise typer.Exit(code=1)

    except typer.Exit:
        raise

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)
