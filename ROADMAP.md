# NexaSec Studio — Roadmap & Checklist

Source of truth for build order. Check items off as we finish them.
Each phase ends with a commit + push (see workflow at the bottom).

---

## M1 — Unify the Pipeline (foundation fix, no new features)

Goal: one project layout, one clip schema, no dead code.

- [ ] Fix `ClipVideo` / `clip_importer.py` schema mismatch (width/height ints, drop stray `codec`/`resolution` keys or add them properly to the dataclass)
- [ ] Add `ClipMetadata.load(path)` (currently only `.save()` exists)
- [ ] Add a `nexasec/core/clip_store.py` (or similar) service to read/update a clip's metadata safely, instead of hand-rolled `json.load`/`json.dump` scattered across services
- [ ] Generalize `sync_audio` / the `audio sync` flow to take **any** clip name, not hardcoded `1.1.mov` / `1.1.wav`
- [ ] Add `nexasec clip attach <project> <clip> video|audio <file>` (image/broll can come in M1.1 if time allows)
- [ ] Remove or merge dead duplicate commands: `commands/build.py` vs `commands/timeline.py`, `commands/audio_sync.py` vs `commands/audio.py`
- [ ] Decide on ONE project layout going forward (multi-clip) and migrate `lesson-001/1.1` + `lesson-002` to match the current `ClipMetadata` schema
- [ ] Add real pytest tests: clip creation, clip import, metadata round-trip (save → load → same data)
- [ ] `device="cuda"` fallback to `cpu` in `transcriber.py` (so tests/CI don't require a GPU)

**Commit checkpoint:** `git commit -m "M1: unify clip pipeline, fix schema mismatches, add clip attach"`

---

## M2 — Per-Clip Audio + Transcription

- [ ] `clip attach ... audio <file>` fully wired (extends M1 attach to microphone audio per clip)
- [ ] `clip sync <project> <clip>` — replace camera audio with mic audio, per clip, output to clip's own folder
- [ ] `clip transcribe <project> <clip>` — WhisperX per clip, output stored under `sources/clips/<clip>/captions/raw/`
- [ ] Batch command: transcribe all clips in a project in one call
- [ ] Tests: sync produces expected output file + duration match; transcribe produces valid segments JSON

**Commit checkpoint:** `git commit -m "M2: per-clip audio sync and transcription"`

---

## M3 — Timeline Engine v2

- [ ] New timeline schema: multiple video **layers** (e.g. screen + facecam overlay), multiple audio layers, captions track, graphics track, effects track
- [ ] Timeline entries reference clips by ID (not raw filenames)
- [ ] `nexasec timeline build <project>` rewritten to assemble from the clip database, honoring each clip's `type`/`role`/`layout` rules (main vs overlay vs supporting)
- [ ] Validation: reject a timeline that references a clip that isn't imported yet
- [ ] Tests: building a timeline from a known clip set produces the expected track structure

**Commit checkpoint:** `git commit -m "M3: multi-layer timeline engine"`

---

## M4 — Caption Engine

- [ ] Arabic correction pass on WhisperX output (fix common Darija/programming-term mis-transcriptions)
- [ ] RTL/LTR mixed rendering (Arabic sentence + embedded English terms like `loop`, `function`, `Python`)
- [ ] Style application from `style.json`: YouTube = bottom clean captions, Shorts = karaoke animated
- [ ] Export to SRT and/or ASS
- [ ] Tests: mixed RTL/LTR sample renders correctly; style config actually changes output

**Commit checkpoint:** `git commit -m "M4: caption engine with RTL/LTR + style-driven output"`

---

## M5 — Motion Graphics Engine

- [ ] Evaluate/confirm HyperFrames integration point (Node.js 22+ subprocess, invoked from Python)
- [ ] Build templates driven by `style.json` (Obsidian & Gold tokens): intro, outro, lower-thirds, chapter cards, code highlights, progress indicator
- [ ] Render templates to transparent overlay clips (WebM/PNG sequence) for later ffmpeg compositing
- [ ] Safe-zone system so graphics don't get clipped when aspect ratio changes
- [ ] Tests/lint: run `hyperframes lint` on generated compositions before considering a template "done"

**Commit checkpoint:** `git commit -m "M5: motion graphics engine (HyperFrames templates)"`

---

## M6 — Render + Export Engine

- [ ] ffmpeg composition builder: timeline → filter graph → rendered video
- [ ] YouTube export: 16:9, 1080p+
- [ ] Shorts export: 9:16, same timeline, responsive graphics repositioning (not a naive crop)
- [ ] `nexasec export youtube <project>` / `nexasec export shorts <project>` commands
- [ ] Tests: render a short known-good timeline end-to-end and assert output file exists with expected duration/resolution

**Commit checkpoint:** `git commit -m "M6: render + export engine, dual 16:9/9:16 output"`

---

## Git Workflow (every phase, every meaningful chunk of work)

After each checklist item or logical group of items is done and verified:

```bash
git add -A
git commit -m "M<phase>: <short description of what changed>"
git push origin main
```

Rules I'll follow:
- Never bundle unrelated changes from two different phases into one commit.
- Commit message always states the phase number so history reads like this checklist.
- I'll tell you explicitly when a phase is fully checked off and ready to push — you just confirm and I run the commands.
- If something breaks mid-phase, we commit working checkpoints, not broken intermediate states, onto `main`. Larger risky changes can go on a branch if you'd rather not touch `main` directly — your call.
