from pathlib import Path
import json

from nexasec.core.clip_store import clip_folder, load_clip
from nexasec.core.style import load_style
from nexasec.core.timeline import Timeline, timeline_path
from nexasec.core.text_correction import apply_glossary
from nexasec.core.bidi_formatter import wrap_ltr_runs, contains_rtl
from nexasec.core.subtitle_writer import (
    build_srt,
    build_ass_header,
    build_ass_dialogue_line,
    build_karaoke_text,
    format_ass_timestamp,
)


def _process_text(text: str) -> str:
    """
    Apply glossary correction, then RTL/LTR bidi wrapping.

    Bidi wrapping is triggered by the text actually containing
    Arabic-script characters, not by the project's language tag --
    Darija is frequently transcribed in Latin/Arabizi script (e.g.
    "salam khawa" rather than "سلام خاوة"), and wrapping plain Latin
    text in isolate marks would just be noise with nothing to isolate
    it from.
    """

    text = apply_glossary(text)

    if contains_rtl(text):
        text = wrap_ltr_runs(text)

    return text


def _transcript_path(project: str, clip_name: str) -> Path:
    return clip_folder(project, clip_name) / "captions" / "raw" / "transcript.json"


def _load_transcript(project: str, clip_name: str) -> dict:

    path = _transcript_path(project, clip_name)

    if not path.exists():
        raise FileNotFoundError(
            f"Clip '{clip_name}' has no transcript yet. Run "
            f"'nexasec clip transcribe {project} {clip_name}' first."
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _youtube_output_dir(project: str) -> Path:
    return Path("projects") / project / "captions" / "youtube"


def build_youtube_captions(project: str) -> tuple[Path, Path, list[str]]:
    """
    Build clean bottom-of-screen YouTube captions (SRT + ASS) for a
    project, timed against its timeline: each clip's transcript
    segments are shifted by that clip's timeline start offset, then
    merged in chronological order across every video layer.

    Clips referenced by the timeline that don't have a transcript
    yet are skipped and reported back as warnings, matching the same
    partial-progress-is-fine convention as clip transcribe-all and
    timeline build.
    """

    timeline = Timeline.load(timeline_path(project))
    style = load_style(project)

    youtube_style = style.get("captions", {}).get("youtube", {})
    font = style.get("fonts", {}).get("body", "Inter")
    font_size = youtube_style.get("size", 48)
    position = youtube_style.get("position", "bottom")
    text_color = style.get("colors", {}).get("text", "#FFFFFF")
    accent_color = style.get("colors", {}).get("gold", "#C6A15B")

    all_clip_refs = [
        (clip_ref.clip, clip_ref.start)
        for layer in timeline.video_layers
        for clip_ref in layer.clips
    ]

    all_clip_refs.sort(key=lambda pair: pair[1])

    merged_segments: list[dict] = []
    warnings: list[str] = []

    for clip_name, clip_start in all_clip_refs:

        try:
            transcript = _load_transcript(project, clip_name)
        except FileNotFoundError as e:
            warnings.append(str(e))
            continue

        for segment in transcript.get("segments", []):

            merged_segments.append({
                "start": segment["start"] + clip_start,
                "end": segment["end"] + clip_start,
                "text": _process_text(segment["text"].strip()),
            })

    output_dir = _youtube_output_dir(project)
    output_dir.mkdir(parents=True, exist_ok=True)

    srt_path = output_dir / "captions.srt"
    srt_path.write_text(
        build_srt(merged_segments),
        encoding="utf-8"
    )

    ass_path = output_dir / "captions.ass"

    ass_content = build_ass_header(
        play_res_x=1920,
        play_res_y=1080,
        font=font,
        font_size=font_size,
        text_color_hex=text_color,
        highlight_color_hex=accent_color,
        position=position,
    )

    for segment in merged_segments:
        ass_content += build_ass_dialogue_line(
            segment["start"],
            segment["end"],
            segment["text"],
        )

    ass_path.write_text(ass_content, encoding="utf-8")

    return srt_path, ass_path, warnings


def build_shorts_captions(project: str, clip_name: str) -> Path:
    """
    Build karaoke-style word-by-word captions (ASS) for a single
    clip, using WhisperX's per-word timestamps. Shorts are built
    per-clip (one bite-sized idea per clip, per the brand brief)
    rather than assembled from the full timeline.
    """

    load_clip(project, clip_name)  # raises if the clip doesn't exist
    style = load_style(project)

    shorts_style = style.get("captions", {}).get("shorts", {})
    font = style.get("fonts", {}).get("body", "Inter")
    font_size = shorts_style.get("size", 72)
    position = shorts_style.get("position", "center")
    text_color = style.get("colors", {}).get("text", "#FFFFFF")
    accent_color = style.get("colors", {}).get("gold", "#C6A15B")

    transcript = _load_transcript(project, clip_name)

    ass_content = build_ass_header(
        play_res_x=1080,
        play_res_y=1920,
        font=font,
        font_size=font_size,
        text_color_hex=text_color,
        highlight_color_hex=accent_color,
        position=position,
        margin_v=250,  # keep clear of platform UI buttons (safe zone)
    )

    for segment in transcript.get("segments", []):

        words = segment.get("words", [])

        # Words without alignment timestamps (WhisperX occasionally
        # can't align a word) can't be karaoke-timed individually --
        # fall back to a plain (non-karaoke) line for that segment
        # rather than dropping it or crashing.
        words = [w for w in words if "start" in w and "end" in w]

        if not words:
            text = _process_text(segment["text"].strip())
            ass_content += build_ass_dialogue_line(
                segment["start"], segment["end"], text
            )
            continue

        needs_bidi = contains_rtl(segment["text"])

        corrected_words = []
        for w in words:
            word_text = apply_glossary(w["word"])
            if needs_bidi:
                word_text = wrap_ltr_runs(word_text)
            corrected_words.append({**w, "word": word_text})

        karaoke_text = build_karaoke_text(corrected_words)

        ass_content += build_ass_dialogue_line(
            segment["start"], segment["end"], karaoke_text
        )

    output_path = (
        clip_folder(project, clip_name)
        / "captions"
        / "rendered"
        / "shorts.ass"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ass_content, encoding="utf-8")

    return output_path
