from nexasec.services.video_analyzer import analyze_video


def test_analyze_video_returns_streams(test_video):

    result = analyze_video(str(test_video))

    assert "streams" in result
    assert len(result["streams"]) > 0
