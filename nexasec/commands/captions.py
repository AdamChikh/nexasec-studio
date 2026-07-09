import typer


app = typer.Typer()


# NOTE: raw transcription now happens per-clip via
# 'nexasec clip transcribe <project> <clip>' (see commands/clip.py).
#
# This command group is reserved for the Caption Engine (M4):
# Arabic correction, RTL/LTR formatting, style-driven caption
# rendering (clean captions for YouTube, karaoke for Shorts), and
# SRT/ASS export -- built on top of the raw transcripts clip
# transcribe already produces.
