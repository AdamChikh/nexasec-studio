import typer
from rich.console import Console
from pathlib import Path

from nexasec.core.clip import create_clip
from nexasec.core.clip_store import clip_folder, load_clip, save_clip
from nexasec.services.clip_attacher import attach as attach_media
from nexasec.services.clip_attacher import SUPPORTED_MEDIA_TYPES
from nexasec.services.clip_syncer import sync_clip
from nexasec.services.clip_transcriber import transcribe_clip, transcribe_all_clips


app = typer.Typer()

console = Console()


@app.command()
def create(
    project: str,
    clip_name: str
):
    """
    Create a new video clip inside a lesson.
    """

    try:

        create_clip(
            project,
            clip_name
        )

        console.print(
            f"[bold green]✔ Clip '{clip_name}' created[/bold green]"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command()
def attach(
    project: str,
    clip_name: str,
    media_type: str,
    file_path: str
):
    """
    Attach a media file to a clip.

    media_type: video | audio

    Example:
        nexasec clip attach lesson-001 1.1 video 1.1.mov
        nexasec clip attach lesson-001 1.1 audio 1.1.wav
    """

    if media_type not in SUPPORTED_MEDIA_TYPES:
        console.print(
            f"[bold red]✖ Unsupported media type '{media_type}'. "
            f"Supported types: {', '.join(SUPPORTED_MEDIA_TYPES)}[/bold red]"
        )
        raise typer.Exit(code=1)

    try:
        output = attach_media(
            project,
            clip_name,
            media_type,
            file_path
        )

        console.print(
            f"[bold green]✔ Attached {media_type}:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command()
def sync(
    project: str,
    clip_name: str,
    offset: float = typer.Option(
        None,
        "--offset",
        help="Manually specify the audio offset in seconds instead of auto-detecting it.",
    ),
):
    """
    Replace a clip's camera audio with its attached microphone
    audio. Requires both video and audio to already be attached
    to the clip.

    By default, automatically detects how far into the audio file
    the video's content actually begins (by cross-correlating the
    video's own built-in audio against the external mic recording)
    and trims accordingly, since camera and mic recordings rarely
    start at exactly the same instant. Use --offset to override this
    if auto-detection gets it wrong.
    """

    try:

        output_path, detected_offset = sync_clip(
            project, clip_name, audio_offset=offset
        )

        console.print(
            f"[bold green]✔ Clip '{clip_name}' synced"
            f" (audio offset: {detected_offset:.2f}s):[/bold green] {output_path}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command()
def transcribe(
    project: str,
    clip_name: str,
    model_size: str = "small"
):
    """
    Transcribe a clip's microphone audio with WhisperX.

    Requires audio to already be attached via 'clip attach ... audio'.
    """

    try:

        output = transcribe_clip(
            project,
            clip_name,
            model_size=model_size
        )

        console.print(
            f"[bold green]✔ Clip '{clip_name}' transcribed:[/bold green] {output}"
        )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)


@app.command(name="transcribe-all")
def transcribe_all(
    project: str,
    model_size: str = "small"
):
    """
    Transcribe every clip in a project that has audio attached.
    Clips without audio yet are skipped.
    """

    try:

        results = transcribe_all_clips(
            project,
            model_size=model_size
        )

        if not results:
            console.print(
                "[yellow]No clips with attached audio found.[/yellow]"
            )
            return

        for clip_name, output in results.items():
            console.print(
                f"[bold green]✔ {clip_name}:[/bold green] {output}"
            )

    except Exception as e:

        console.print(
            f"[bold red]✖ {e}[/bold red]"
        )

        raise typer.Exit(code=1)
