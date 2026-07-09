import json

import pytest

from nexasec.core.clip import create_clip
from nexasec.core.clip_store import clip_folder, load_clip
from nexasec.services.clip_attacher import attach_audio
from nexasec.services import clip_transcriber


def _fake_transcribe_audio(audio_path, output_path, model_size="small"):
    """
    Stand-in for the real WhisperX call: writes a minimal valid
    transcript so we can test path resolution and status updates
    without needing torch/whisperx/a GPU in the test environment.
    """

    from pathlib import Path

    Path(output_path).write_text(
        json.dumps({"segments": [{"text": "hello", "start": 0.0, "end": 1.0}]})
    )


@pytest.fixture(autouse=True)
def stub_whisperx(monkeypatch):
    monkeypatch.setattr(
        clip_transcriber,
        "transcribe_audio",
        _fake_transcribe_audio
    )


def test_transcribe_clip_writes_output_and_updates_status(isolated_cwd, test_audio):

    create_clip("lesson-001", "1.1")
    attach_audio("lesson-001", "1.1", str(test_audio))

    output = clip_transcriber.transcribe_clip("lesson-001", "1.1")

    assert output.exists()

    data = json.loads(output.read_text())
    assert "segments" in data

    metadata = load_clip("lesson-001", "1.1")
    assert metadata.status == "transcribed"


def test_transcribe_clip_output_path_is_under_clip_captions(isolated_cwd, test_audio):

    create_clip("lesson-001", "1.1")
    attach_audio("lesson-001", "1.1", str(test_audio))

    output = clip_transcriber.transcribe_clip("lesson-001", "1.1")

    expected = (
        clip_folder("lesson-001", "1.1")
        / "captions"
        / "raw"
        / "transcript.json"
    )

    assert output == expected


def test_transcribe_clip_without_audio_raises(isolated_cwd):

    create_clip("lesson-001", "1.1")

    with pytest.raises(ValueError, match="no audio attached"):
        clip_transcriber.transcribe_clip("lesson-001", "1.1")


def test_transcribe_all_skips_clips_without_audio(isolated_cwd, test_audio):

    create_clip("lesson-001", "1.1")
    attach_audio("lesson-001", "1.1", str(test_audio))

    create_clip("lesson-001", "2.1")  # no audio attached

    results = clip_transcriber.transcribe_all_clips("lesson-001")

    assert "1.1" in results
    assert "2.1" not in results


def test_transcribe_all_missing_project_raises(isolated_cwd):

    with pytest.raises(FileNotFoundError):
        clip_transcriber.transcribe_all_clips("does-not-exist")
