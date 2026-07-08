from nexasec.models.video import VideoMetadata


def parse_video_metadata(
    data: dict,
    filename: str
) -> VideoMetadata:

    video_stream = None
    audio_stream = None

    for stream in data["streams"]:
        if stream["codec_type"] == "video":
            video_stream = stream

        if stream["codec_type"] == "audio":
            audio_stream = stream


    fps = video_stream["avg_frame_rate"]

    numerator, denominator = fps.split("/")

    fps_value = float(numerator) / float(denominator)


    return VideoMetadata(
        filename=filename,
        duration=float(video_stream["duration"]),
        width=video_stream["width"],
        height=video_stream["height"],
        fps=fps_value,
        video_codec=video_stream["codec_name"],
        audio_codec=(
            audio_stream["codec_name"]
            if audio_stream
            else None
        ),
    )
