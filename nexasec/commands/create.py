import typer
from rich.console import Console

from nexasec.core.project import create_project

console = Console()

app = typer.Typer()


@app.command()
def project(name: str):
    create_project(name)
    console.print(f"[bold green]✔ Project '{name}' created successfully![/bold green]")