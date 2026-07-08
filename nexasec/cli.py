import typer

from nexasec.commands.create import app as create_app
from nexasec.commands.import_video import app as import_app
from nexasec.commands.audio import app as audio_app


app = typer.Typer(
    help="🚀 NexaSec Studio"
)


app.add_typer(
    create_app,
    name="create"
)

app.add_typer(
    import_app,
    name="import"
)

app.add_typer(
    audio_app,
    name="audio"
)


if __name__ == "__main__":
    app()
