import typer
from rich.console import Console

console = Console()

app = typer.Typer()


@app.command()
def project(name: str):
    console.print(f"[green]Creating project:[/green] {name}")