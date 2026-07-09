from nexasec.core.clip import create_clip
from nexasec.core.clip_store import clip_folder, load_clip
from nexasec.services.clip_attacher import attach_video, attach_audio
from nexasec.services.audio_sync import sync_audio


def test_sync_produces_output_video(isolated_cwd, test_video, test_audio):

    create_clip("lesson-001", "1.1")

    attach_video("lesson-001", "1.1", str(test_video))
    attach_audio("lesson-001", "1.1", str(test_audio))

    metadata = load_clip("lesson-001", "1.1")

    folder = clip_folder("lesson-001", "1.1")
    video_path = folder / "video" / metadata.video.file
    audio_path = folder / "audio" / metadata.audio.file
    output_path = folder / "video" / "synced.mp4"

    result = sync_audio(
        str(video_path),
        str(audio_path),
        str(output_path)
    )

    assert result.exists()
    assert result.stat().st_size > 0
