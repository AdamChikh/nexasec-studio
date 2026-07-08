from nexasec.services.video_analyzer import analyze_video


result = analyze_video(
    "tests/assets/test-video.mp4"
)

print(result)
