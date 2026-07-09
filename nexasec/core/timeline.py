from pathlib import Path

from nexasec.core.clip_store import load_clip
from nexasec.models.timeline import Timeline, VideoLayer, AudioLayer, ClipRef


TIMELINE_PATH_PARTS = ("timeline", "timeline.json")

# Maps (clip.type, clip.role) -> which video layer a clip belongs on.
# This is the concrete rule for "screen recording as the base layer,
# facecam stacked on top as an overlay" from the project spec.
LAYER_RULES = {
    ("camera", "main"): ("main", "main"),
    ("camera", "overlay"): ("facecam-overlay", "overlay"),
    ("screen", "supporting"): ("screen", "supporting"),
    ("screen", "main"): ("screen", "main"),
}

DEFAULT_LAYER = ("main", "main")


def timeline_path(project: str) -> Path:
    path = Path("projects") / project
    for part in TIMELINE_PATH_PARTS:
        path = path / part
    return path


def create_timeline(project: str) -> Path:
    """
    Create an empty v2 timeline for a project.
    """

    path = timeline_path(project)
    Timeline().save(path)
    return path


def _natural_sort_key(clip_name: str):
    """
    Sort clip names like "1.1", "2.1", "2.10", "10.1" in the order a
    human would expect, not lexical string order (which would put
    "2.10" before "2.2").
    """

    parts = clip_name.split(".")

    key = []
    for part in parts:
        try:
            key.append((0, int(part)))
        except ValueError:
            key.append((1, part))

    return key


def _layer_for(clip_type: str, clip_role: str) -> tuple[str, str]:
    return LAYER_RULES.get((clip_type, clip_role), DEFAULT_LAYER)


def build_timeline(project: str) -> tuple[Path, list[str]]:
    """
    Build a timeline by placing every imported clip in a project
    onto the video layer implied by its type/role, sequentially in
    clip-name order.

    Clips without video attached yet are skipped (not errored) and
    reported back as warnings, so a partially-imported project can
    still produce a usable timeline for what's ready.

    NOTE: clips are placed sequentially, one after another, even
    across different layers. Today's clip model is one file per
    numbered slot, so there's no way yet to express "this screen
    recording and this facecam overlay happened at the same moment"
    as two separate synced clips -- that's a future clip-pairing
    feature, not something this builder can infer on its own.
    """

    clips_root = Path("projects") / project / "sources" / "clips"

    if not clips_root.exists():
        raise FileNotFoundError(f"Project '{project}' has no clips yet.")

    clip_names = sorted(
        (p.name for p in clips_root.iterdir() if p.is_dir()),
        key=_natural_sort_key,
    )

    timeline = Timeline()
    layers_by_name: dict[str, VideoLayer] = {}
    warnings: list[str] = []
    cursor = 0.0

    for clip_name in clip_names:

        metadata = load_clip(project, clip_name)

        if not metadata.video.file or metadata.video.duration is None:
            warnings.append(
                f"Skipped '{clip_name}': no video attached yet."
            )
            continue

        layer_name, layer_role = _layer_for(metadata.type, metadata.role)

        if layer_name not in layers_by_name:
            layer = VideoLayer(name=layer_name, role=layer_role)
            layers_by_name[layer_name] = layer
            timeline.video_layers.append(layer)

        layers_by_name[layer_name].clips.append(
            ClipRef(
                clip=clip_name,
                start=cursor,
                duration=metadata.video.duration,
            )
        )

        cursor += metadata.video.duration

    path = timeline_path(project)
    timeline.save(path)

    return path, warnings


def validate_timeline(project: str) -> list[str]:
    """
    Check that every clip a saved timeline references still exists
    and has video attached. Returns a list of error strings; an
    empty list means the timeline is valid.
    """

    path = timeline_path(project)
    timeline = Timeline.load(path)

    errors: list[str] = []

    for layer in timeline.video_layers:
        for clip_ref in layer.clips:
            try:
                metadata = load_clip(project, clip_ref.clip)
            except FileNotFoundError:
                errors.append(
                    f"Layer '{layer.name}' references clip "
                    f"'{clip_ref.clip}' which no longer exists."
                )
                continue

            if not metadata.video.file:
                errors.append(
                    f"Layer '{layer.name}' references clip "
                    f"'{clip_ref.clip}' which has no video attached."
                )

    return errors
