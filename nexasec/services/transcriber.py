from pathlib import Path
import json
import torch
import whisperx


def _resolve_device() -> str:
    """
    Prefer CUDA when available (production box has PyTorch CUDA),
    but fall back to CPU so this doesn't hard-crash on machines
    without a GPU (e.g. CI, or testing this module in isolation).
    """

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def transcribe_audio(
    audio_path: str,
    output_path: str,
    model_size: str = "small",
    device: str | None = None
):

    device = device or _resolve_device()

    compute_type = "float16" if device == "cuda" else "int8"

    print(f"Loading WhisperX model on '{device}'...")

    model = whisperx.load_model(
        model_size,
        device=device,
        compute_type=compute_type
    )

    print("Loading audio...")

    audio = whisperx.load_audio(
        audio_path
    )

    print("Transcribing...")

    result = model.transcribe(
        audio
    )

    print("Loading alignment model...")

    align_model, metadata = whisperx.load_align_model(
        language_code=result["language"],
        device=device
    )

    print("Aligning words...")

    aligned_result = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio,
        device,
        return_char_alignments=False
    )


    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            aligned_result,
            file,
            indent=4,
            ensure_ascii=False
        )


    return aligned_result