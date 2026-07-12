from pathlib import Path
import subprocess
import wave

import numpy as np
import pytest

from nexasec.services.audio_aligner import find_audio_offset, _extract_mono_pcm


SAMPLE_RATE = 8000


def _write_wav(path: Path, samples: np.ndarray, sample_rate: int = SAMPLE_RATE):

    samples_int16 = np.clip(samples, -32000, 32000).astype(np.int16)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples_int16.tobytes())


def _make_distinctive_signal(rng, n_samples: int) -> np.ndarray:
    """
    A noise burst is a good stand-in for real speech for correlation
    testing purposes -- it has a distinctive, non-repeating waveform
    shape (unlike a pure tone, which would correlate ambiguously at
    multiple periodic offsets).
    """

    return rng.uniform(-10000, 10000, size=n_samples)


def test_find_audio_offset_recovers_known_offset(tmp_path):

    rng = np.random.default_rng(seed=42)

    reference_duration_samples = SAMPLE_RATE * 2  # 2s "take"
    known_offset_seconds = 5.3

    reference = _make_distinctive_signal(rng, reference_duration_samples)

    padding_before = rng.uniform(-500, 500, size=int(known_offset_seconds * SAMPLE_RATE))
    padding_after = rng.uniform(-500, 500, size=SAMPLE_RATE * 3)

    external = np.concatenate([padding_before, reference, padding_after])

    ref_path = tmp_path / "reference.wav"
    ext_path = tmp_path / "external.wav"

    _write_wav(ref_path, reference)
    _write_wav(ext_path, external)

    detected_offset = find_audio_offset(str(ref_path), str(ext_path))

    # allow small tolerance for sample-rounding
    assert abs(detected_offset - known_offset_seconds) < 0.05


def test_find_audio_offset_zero_offset(tmp_path):
    """
    Reference content starting immediately at sample 0 of external
    (external is just reference + trailing padding).
    """

    rng = np.random.default_rng(seed=7)

    reference = _make_distinctive_signal(rng, SAMPLE_RATE * 2)
    trailing = rng.uniform(-500, 500, size=SAMPLE_RATE * 2)

    external = np.concatenate([reference, trailing])

    ref_path = tmp_path / "reference.wav"
    ext_path = tmp_path / "external.wav"

    _write_wav(ref_path, reference)
    _write_wav(ext_path, external)

    detected_offset = find_audio_offset(str(ref_path), str(ext_path))

    assert abs(detected_offset - 0.0) < 0.05


def test_find_audio_offset_different_known_offsets(tmp_path):
    """
    Sweep a few different known offsets to make sure the first test
    passing wasn't a fluke of that specific offset value.
    """

    for known_offset_seconds in (0.8, 12.4, 30.0):

        rng = np.random.default_rng(seed=int(known_offset_seconds * 100))

        reference = _make_distinctive_signal(rng, SAMPLE_RATE * 2)
        padding_before = rng.uniform(-500, 500, size=int(known_offset_seconds * SAMPLE_RATE))
        padding_after = rng.uniform(-500, 500, size=SAMPLE_RATE * 2)

        external = np.concatenate([padding_before, reference, padding_after])

        ref_path = tmp_path / f"reference_{known_offset_seconds}.wav"
        ext_path = tmp_path / f"external_{known_offset_seconds}.wav"

        _write_wav(ref_path, reference)
        _write_wav(ext_path, external)

        detected_offset = find_audio_offset(str(ref_path), str(ext_path))

        assert abs(detected_offset - known_offset_seconds) < 0.05, (
            f"expected ~{known_offset_seconds}s, got {detected_offset}s"
        )


def test_extract_mono_pcm_works_on_real_video_via_ffmpeg(test_video):
    """
    Integration check that the ffmpeg extraction path itself works
    end to end on a real video file, not just synthetic WAVs.
    """

    samples = _extract_mono_pcm(str(test_video), SAMPLE_RATE)

    assert len(samples) > 0
    # 5s test video at 8kHz should yield roughly 40000 samples
    assert 35000 < len(samples) < 45000


def test_extract_mono_pcm_raises_on_video_with_no_audio(tmp_path):

    video_only = tmp_path / "video_only.mp4"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=1:size=320x240:rate=30",
            "-c:v", "libx264", "-preset", "ultrafast",
            str(video_only),
        ],
        check=True,
        capture_output=True,
    )

    with pytest.raises(RuntimeError):
        _extract_mono_pcm(str(video_only), SAMPLE_RATE)
