import pytest

from nexasec.core.clip import create_clip
from nexasec.core.clip_store import load_clip, save_clip
from nexasec.core.timeline import (
    create_timeline,
    build_timeline,
    validate_timeline,
    timeline_path,
)
from nexasec.models.timeline import Timeline, VideoLayer, AudioLayer, ClipRef
from nexasec.services.clip_attacher import attach_video


def _make_imported_clip(project, name, clip_type="camera", role="main", duration=5.0):
    """
    Create a clip and fake it into an "imported" state without
    needing a real video file -- timeline logic only reads
    metadata.video.file/duration, so this is enough for these tests.
    """

    create_clip(project, name)
    metadata = load_clip(project, name)
    metadata.type = clip_type
    metadata.role = role
    metadata.video.file = f"{name}.mov"
    metadata.video.duration = duration
    metadata.status = "imported"
    save_clip(project, name, metadata)


def test_create_timeline_writes_empty_v2_schema(isolated_cwd):

    path = create_timeline("lesson-001")

    timeline = Timeline.load(path)

    assert timeline.version == 2
    assert timeline.video_layers == []
    assert timeline.audio_layers == []


def test_timeline_round_trip(tmp_path):

    original = Timeline(
        fps=30.0,
        video_layers=[
            VideoLayer(
                name="screen",
                role="supporting",
                clips=[ClipRef(clip="1.2", start=0.0, duration=4.0)],
            )
        ],
        audio_layers=[
            AudioLayer(
                name="mic",
                clips=[ClipRef(clip="1.2", start=0.0, duration=4.0)],
            )
        ],
    )

    path = tmp_path / "timeline.json"
    original.save(path)

    loaded = Timeline.load(path)

    assert loaded == original


def test_build_places_talking_head_clips_on_main_layer(isolated_cwd):

    _make_imported_clip("lesson-001", "1.1", clip_type="camera", role="main", duration=5.0)
    _make_imported_clip("lesson-001", "2.1", clip_type="camera", role="main", duration=3.0)

    path, warnings = build_timeline("lesson-001")

    timeline = Timeline.load(path)

    assert warnings == []
    assert len(timeline.video_layers) == 1

    main_layer = timeline.video_layers[0]
    assert main_layer.name == "main"
    assert [c.clip for c in main_layer.clips] == ["1.1", "2.1"]

    # sequential placement: second clip starts where the first ends
    assert main_layer.clips[0].start == 0.0
    assert main_layer.clips[1].start == 5.0


def test_build_splits_screen_and_overlay_into_separate_layers(isolated_cwd):

    _make_imported_clip("lesson-002", "1.2", clip_type="screen", role="supporting", duration=10.0)
    _make_imported_clip("lesson-002", "1.4", clip_type="camera", role="overlay", duration=3.0)

    path, warnings = build_timeline("lesson-002")

    timeline = Timeline.load(path)

    layer_names = {layer.name for layer in timeline.video_layers}
    assert layer_names == {"screen", "facecam-overlay"}

    screen_layer = next(l for l in timeline.video_layers if l.name == "screen")
    overlay_layer = next(l for l in timeline.video_layers if l.name == "facecam-overlay")

    assert screen_layer.role == "supporting"
    assert overlay_layer.role == "overlay"
    assert screen_layer.clips[0].clip == "1.2"
    assert overlay_layer.clips[0].clip == "1.4"


def test_build_uses_natural_clip_order_not_lexical(isolated_cwd):

    # lexically "2.10" < "2.2", but naturally 2.2 should come first
    _make_imported_clip("lesson-001", "2.10", duration=1.0)
    _make_imported_clip("lesson-001", "2.2", duration=1.0)
    _make_imported_clip("lesson-001", "1.1", duration=1.0)

    path, warnings = build_timeline("lesson-001")

    timeline = Timeline.load(path)
    order = [c.clip for c in timeline.video_layers[0].clips]

    assert order == ["1.1", "2.2", "2.10"]


def test_build_skips_clips_without_video_and_warns(isolated_cwd):

    _make_imported_clip("lesson-001", "1.1", duration=5.0)
    create_clip("lesson-001", "2.1")  # no video attached

    path, warnings = build_timeline("lesson-001")

    timeline = Timeline.load(path)

    assert [c.clip for c in timeline.video_layers[0].clips] == ["1.1"]
    assert len(warnings) == 1
    assert "2.1" in warnings[0]


def test_build_missing_project_raises(isolated_cwd):

    with pytest.raises(FileNotFoundError):
        build_timeline("does-not-exist")


def test_validate_passes_for_clean_timeline(isolated_cwd):

    _make_imported_clip("lesson-001", "1.1", duration=5.0)
    build_timeline("lesson-001")

    errors = validate_timeline("lesson-001")

    assert errors == []


def test_validate_catches_clip_that_lost_its_video(isolated_cwd):

    _make_imported_clip("lesson-001", "1.1", duration=5.0)
    build_timeline("lesson-001")

    # simulate the clip's video being un-attached after the timeline
    # was already built
    metadata = load_clip("lesson-001", "1.1")
    metadata.video.file = None
    save_clip("lesson-001", "1.1", metadata)

    errors = validate_timeline("lesson-001")

    assert len(errors) == 1
    assert "1.1" in errors[0]


def test_validate_catches_deleted_clip(isolated_cwd):

    _make_imported_clip("lesson-001", "1.1", duration=5.0)
    build_timeline("lesson-001")

    import shutil
    from nexasec.core.clip_store import clip_folder
    shutil.rmtree(clip_folder("lesson-001", "1.1"))

    errors = validate_timeline("lesson-001")

    assert len(errors) == 1
    assert "no longer exists" in errors[0]
