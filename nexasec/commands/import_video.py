
import typer

from rich.console import Console



from nexasec.services.video_importer import import_video



console = Console()



app = typer.Typer()





@app.command()

def video(

    project: str,

    path: str,

):

    """

    Import a source video into a project.

    """



    try:

        import_video(project, path)

        console.print(f"[bold green]✔ Video imported into '{project}'[/bold green]")

    except Exception as e:

        console.print(f"[bold red]✖ {e}[/bold red]")

        raise typer.Exit(code=1)

