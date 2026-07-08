import typer
from pathlib import Path

from nexasec.services.transcriber import transcribe_audio


app = typer.Typer()


@app.command()
def generate(
    project: str
):

    audio = (
        Path("projects")
        / project
        / "assets"
        / "audio"
        / "source.wav"
    )

    output = (
        Path("projects")
        / project
        / "captions"
        / "raw"
        / "transcript.json"
    )


    transcribe_audio(
        str(audio),
        str(output)
    )


    print("✔ Captions generated")
