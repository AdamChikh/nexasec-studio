def format_srt_timestamp(seconds: float) -> str:
    """
    Format seconds as an SRT timestamp: HH:MM:SS,mmm
    """

    if seconds < 0:
        seconds = 0

    total_ms = round(seconds * 1000)

    hours, remainder_ms = divmod(total_ms, 3_600_000)
    minutes, remainder_ms = divmod(remainder_ms, 60_000)
    secs, ms = divmod(remainder_ms, 1_000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def format_ass_timestamp(seconds: float) -> str:
    """
    Format seconds as an ASS timestamp: H:MM:SS.cc (centiseconds)
    """

    if seconds < 0:
        seconds = 0

    total_cs = round(seconds * 100)

    hours, remainder_cs = divmod(total_cs, 360_000)
    minutes, remainder_cs = divmod(remainder_cs, 6_000)
    secs, cs = divmod(remainder_cs, 100)

    return f"{hours:d}:{minutes:02d}:{secs:02d}.{cs:02d}"


def build_srt(segments: list[dict]) -> str:
    """
    Build SRT content from a list of {start, end, text} segments.
    """

    lines = []

    for index, segment in enumerate(segments, start=1):

        lines.append(str(index))
        lines.append(
            f"{format_srt_timestamp(segment['start'])} --> "
            f"{format_srt_timestamp(segment['end'])}"
        )
        lines.append(segment["text"].strip())
        lines.append("")

    return "\n".join(lines)


def hex_to_ass_color(hex_color: str, alpha: int = 0) -> str:
    """
    Convert a "#RRGGBB" hex color to ASS's "&HAABBGGRR" format.
    ASS alpha is inverted: 00 = fully opaque, FF = fully transparent.
    """

    hex_color = hex_color.lstrip("#")

    r = hex_color[0:2]
    g = hex_color[2:4]
    b = hex_color[4:6]

    return f"&H{alpha:02X}{b.upper()}{g.upper()}{r.upper()}"


ASS_ALIGNMENT = {
    "bottom": 2,   # bottom-center
    "center": 5,   # middle-center
    "top": 8,      # top-center
}


def build_ass_header(
    play_res_x: int,
    play_res_y: int,
    font: str,
    font_size: int,
    text_color_hex: str,
    highlight_color_hex: str,
    position: str,
    margin_v: int = 60,
) -> str:
    """
    Build the [Script Info] and [V4+ Styles] sections of an ASS file.
    A single "Default" style is defined; PrimaryColour is used for
    unhighlighted text, SecondaryColour for the karaoke highlight
    color (the {\\k} tag switches from Secondary to Primary as each
    word plays).
    """

    alignment = ASS_ALIGNMENT.get(position, 2)

    primary = hex_to_ass_color(text_color_hex)
    secondary = hex_to_ass_color(highlight_color_hex)
    outline = "&H00000000"
    back = "&H64000000"

    return (
        "[Script Info]\n"
        "Title: NexaSec Captions\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {play_res_x}\n"
        f"PlayResY: {play_res_y}\n"
        "ScaledBorderAndShadow: yes\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{font},{font_size},{primary},{secondary},"
        f"{outline},{back},0,0,0,0,100,100,0,0,1,2,0,{alignment},"
        f"40,40,{margin_v},1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "MarginV, Effect, Text\n"
    )


def build_ass_dialogue_line(start: float, end: float, text: str) -> str:

    return (
        f"Dialogue: 0,{format_ass_timestamp(start)},"
        f"{format_ass_timestamp(end)},Default,,0,0,0,,{text}\n"
    )


def build_karaoke_text(words: list[dict]) -> str:
    """
    Build ASS karaoke tag text from a list of
    {"word": str, "start": float, "end": float} entries. Each word
    gets a {\\k<centiseconds>} tag for how long it stays highlighted
    before the next word takes over.
    """

    parts = []

    for word in words:

        duration_cs = max(
            1,
            round((word["end"] - word["start"]) * 100)
        )

        parts.append(f"{{\\k{duration_cs}}}{word['word']}")

    return " ".join(parts)
