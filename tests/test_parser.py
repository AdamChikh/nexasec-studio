from nexasec.services.video_analyzer import analyze_video
from nexasec.services.video_parser import parse_video_metadata


def test_parse_video_metadata(test_video):

    data = analyze_video(str(test_video))

    metadata = parse_video_metadata(data, test_video.name)

    assert metadata.filename == test_video.name
    assert metadata.duration > 0
    assert metadata.width > 0
    assert metadata.height > 0
    assert metadata.fps > 0
    assert metadata.video_codec is not None
