import json

from nexasec.models.clip import ClipMetadata, ClipVideo, ClipAudio


def test_save_then_load_round_trip(tmp_path):

    original = ClipMetadata(
        name="1.1",
        type="camera",
        role="main",
        status="imported",
        video=ClipVideo(
            file="1.1.mov",
            duration=12.5,
            width=1920,
            height=1080,
            fps=30.0,
            codec="prores",
        ),
        audio=ClipAudio(
            file="1.1.wav",
            type="microphone",
            sample_rate=48000,
        ),
    )

    path = tmp_path / "metadata.json"
    original.save(path)

    loaded = ClipMetadata.load(path)

    assert loaded == original


def test_load_missing_file_raises(tmp_path):

    missing = tmp_path / "does-not-exist.json"

    try:
        ClipMetadata.load(missing)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_load_old_flat_schema_falls_back_to_defaults(tmp_path):
    """
    Clips created before the type/role/layout fields existed
    (e.g. lesson-001's original 1.1 clip) must still load without
    crashing.
    """

    old_schema = {
        "name": "1.1",
        "status": "raw",
        "video": None,
        "audio": None,
        "captions": None,
    }

    path = tmp_path / "metadata.json"
    path.write_text(json.dumps(old_schema))

    loaded = ClipMetadata.load(path)

    assert loaded.name == "1.1"
    assert loaded.status == "raw"
    assert loaded.type == "camera"  # default
    assert loaded.role == "main"  # default
    assert loaded.video.file is None
    assert loaded.audio.file is None


def test_video_metadata_shape_matches_importer_output():
    """
    Regression test for the M1 schema-mismatch bug: ClipVideo must
    accept width/height as ints and a codec field, matching exactly
    what services/clip_attacher.py writes.
    """

    video = ClipVideo(
        file="1.1.mov",
        duration=10.0,
        width=1920,
        height=1080,
        fps=29.97,
        codec="h264",
    )

    assert video.width == 1920
    assert video.height == 1080
    assert video.codec == "h264"
