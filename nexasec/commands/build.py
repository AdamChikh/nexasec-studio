import typer
from rich.console import Console

from nexasec.core.timeline_builder import build_timeline


app = typer.Typer()

console = Console()


@app.command()
def timeline(
    project: str
):

    path = build_timeline(project)

    console.print(
        f"[bold green]✔ Timeline built:[/bold green] {path}"
    )
