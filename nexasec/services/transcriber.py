from pathlib import Path
import json
import whisperx


def transcribe_audio(
    audio_path: str,
    output_path: str,
    model_size: str = "small"
):

    device = "cuda"

    print("Loading WhisperX model...")

    model = whisperx.load_model(
        model_size,
        device=device,
        compute_type="float16"
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