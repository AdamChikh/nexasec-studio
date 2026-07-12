from pathlib import Path
import subprocess
import tempfile
import wave

import numpy as np


def _extract_mono_pcm(input_path: str, target_sample_rate: int) -> np.ndarray:
    """
    Use ffmpeg to extract the audio from any input (video or audio
    file) as mono PCM16 at a low sample rate -- we don't need audio
    fidelity for alignment, just timing, so a low rate keeps the
    cross-correlation fast.

    Raises RuntimeError if the input has no audio stream at all.
    """

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:

        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(input_path),
                "-vn",
                "-ac", "1",
                "-ar", str(target_sample_rate),
                "-f", "wav",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Could not extract audio from '{input_path}' -- it "
                f"may have no audio stream:\n{result.stderr}"
            )

        with wave.open(str(tmp_path), "rb") as wav_file:
            n_frames = wav_file.getnframes()
            raw = wav_file.readframes(n_frames)

        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)

        if len(samples) == 0:
            raise RuntimeError(
                f"'{input_path}' produced no audio samples -- it "
                f"likely has no audio stream."
            )

        return samples

    finally:
        tmp_path.unlink(missing_ok=True)


def find_audio_offset(
    reference_path: str,
    external_path: str,
    max_offset_seconds: float = 300.0,
    sample_rate: int = 8000,
) -> float:
    """
    Find how many seconds into external_path its audio content best
    aligns with the start of reference_path's audio, using FFT-based
    cross-correlation.

    Typical use: reference_path is a clip's own camera video (whose
    built-in mic captured a lower-quality but time-accurate reference
    of the take), external_path is a separate, longer external mic
    recording that may have been started earlier and/or cover more
    than just this one clip. The returned offset is where to trim
    external_path so it starts at the same moment as reference_path.

    This only searches for non-negative offsets (external recording
    started at or before the reference) -- the far more common case
    in practice (mic rolling before camera starts recording).
    """

    reference = _extract_mono_pcm(reference_path, sample_rate)
    external = _extract_mono_pcm(external_path, sample_rate)

    # zero-mean to remove DC bias so correlation reflects actual
    # waveform shape, not just overall signal level
    reference = reference - reference.mean()
    external = external - external.mean()

    n = len(external) + len(reference) - 1
    nfft = 1
    while nfft < n:
        nfft *= 2

    fft_external = np.fft.rfft(external, nfft)
    fft_reference = np.fft.rfft(reference, nfft)

    # corr[k] = sum_n external[n+k] * reference[n] for the valid
    # (non-wraparound) range k = 0 .. len(external)-1, i.e. how well
    # reference matches external starting at sample offset k
    correlation = np.fft.irfft(fft_external * np.conj(fft_reference), nfft)

    max_offset_samples = min(
        len(external),
        int(max_offset_seconds * sample_rate),
    )

    search_window = correlation[:max_offset_samples]

    best_offset_samples = int(np.argmax(search_window))

    return best_offset_samples / sample_rate
