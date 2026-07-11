from nexasec.core.subtitle_writer import (
    format_srt_timestamp,
    format_ass_timestamp,
    build_srt,
    hex_to_ass_color,
    build_ass_header,
    build_ass_dialogue_line,
    build_karaoke_text,
)


def test_srt_timestamp_format():
    assert format_srt_timestamp(0) == "00:00:00,000"
    assert format_srt_timestamp(65.5) == "00:01:05,500"
    assert format_srt_timestamp(3661.25) == "01:01:01,250"


def test_srt_timestamp_negative_clamped_to_zero():
    assert format_srt_timestamp(-1) == "00:00:00,000"


def test_ass_timestamp_format():
    assert format_ass_timestamp(0) == "0:00:00.00"
    assert format_ass_timestamp(65.5) == "0:01:05.50"
    assert format_ass_timestamp(3661.25) == "1:01:01.25"


def test_build_srt_produces_sequential_indices():
    segments = [
        {"start": 0.0, "end": 1.0, "text": "hello"},
        {"start": 1.0, "end": 2.0, "text": "world"},
    ]
    result = build_srt(segments)
    assert "1\n00:00:00,000 --> 00:00:01,000\nhello" in result
    assert "2\n00:00:01,000 --> 00:00:02,000\nworld" in result


def test_hex_to_ass_color_conversion():
    # ASS format is &HAABBGGRR -- reversed byte order from #RRGGBB
    assert hex_to_ass_color("#FFFFFF") == "&H00FFFFFF"
    assert hex_to_ass_color("#0A0A0C") == "&H000C0A0A"
    assert hex_to_ass_color("#C6A15B") == "&H005BA1C6"


def test_ass_header_contains_correct_alignment():
    header = build_ass_header(
        play_res_x=1920, play_res_y=1080,
        font="Inter", font_size=48,
        text_color_hex="#FFFFFF", highlight_color_hex="#C6A15B",
        position="bottom",
    )
    assert "PlayResX: 1920" in header
    # bottom-center is ASS alignment code 2; field order is
    # ...,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,...
    # i.e. "...,1,2,0,<alignment>,40,40,..."
    assert ",1,2,0,2,40,40," in header


def test_ass_header_center_alignment_for_shorts():
    header = build_ass_header(
        play_res_x=1080, play_res_y=1920,
        font="Inter", font_size=72,
        text_color_hex="#FFFFFF", highlight_color_hex="#C6A15B",
        position="center",
    )
    # middle-center is ASS alignment code 5
    assert ",1,2,0,5,40,40," in header


def test_karaoke_text_duration_in_centiseconds():
    words = [
        {"word": "hello", "start": 0.0, "end": 0.5},
        {"word": "world", "start": 0.5, "end": 1.2},
    ]
    result = build_karaoke_text(words)
    assert result == r"{\k50}hello {\k70}world"


def test_karaoke_text_minimum_duration_is_one_centisecond():
    # zero or negative duration words shouldn't produce a {\k0} tag
    words = [{"word": "x", "start": 1.0, "end": 1.0}]
    result = build_karaoke_text(words)
    assert result == r"{\k1}x"


def test_dialogue_line_format():
    line = build_ass_dialogue_line(1.0, 2.5, "hello world")
    assert line.startswith("Dialogue: 0,0:00:01.00,0:00:02.50,Default,,0,0,0,,hello world")
