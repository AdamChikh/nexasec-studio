from nexasec.services.video_analyzer import analyze_video
from nexasec.services.video_parser import parse_video_metadata


data = analyze_video(
    "tests/assets/test-video.mp4"
)

metadata = parse_video_metadata(
    data,
    "test-video.mp4"
)

print(metadata)
