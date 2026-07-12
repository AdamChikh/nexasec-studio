import typer

from nexasec.commands.create import app as create_app
from nexasec.commands.import_video import app as import_app
from nexasec.commands.audio import app as audio_app
from nexasec.commands.captions import app as captions_app
from nexasec.commands.timeline import app as timeline_app
from nexasec.commands.clip import app as clip_app
from nexasec.commands.graphics import app as graphics_app
from nexasec.commands.export import app as export_app


app = typer.Typer(
    help="🚀 NexaSec Studio"
)


app.add_typer(create_app, name="create")
app.add_typer(import_app, name="import")
app.add_typer(audio_app, name="audio")
app.add_typer(captions_app, name="captions")
app.add_typer(timeline_app, name="timeline")
app.add_typer(clip_app, name="clip")
app.add_typer(graphics_app, name="graphics")
app.add_typer(export_app, name="export")


if __name__ == "__main__":
    app()
