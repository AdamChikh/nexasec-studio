import typer

from nexasec.commands.create import app as create_app

app = typer.Typer(
    help="🚀 NexaSec Studio"
)

app.add_typer(
    create_app,
    name="create",
)

if __name__ == "__main__":
    app()