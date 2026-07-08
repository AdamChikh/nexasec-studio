import typer
from rich.console import Console

from nexasec.core.timeline import create_timeline


app = typer.Typer()

console = Console()


@app.command()
def init(
    project: str
):
    """
    Initialize project timeline.
    """

    path = create_timeline(project)

    console.print(
        f"[bold green]✔ Timeline created:[/bold green] {path}"
    )
