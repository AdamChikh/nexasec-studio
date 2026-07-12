from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

import pytest

from nexasec.services import motion_graphics


def _fake_completed_process(returncode=0, stdout="", stderr=""):
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


def test_check_hyperframes_available_raises_when_node_missing():

    with patch("shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="Node.js"):
            motion_graphics.check_hyperframes_available()


def test_check_hyperframes_available_passes_when_both_present():

    with patch("shutil.which", return_value="/usr/bin/node"):
        motion_graphics.check_hyperframes_available()  # should not raise


def test_render_composition_missing_template_raises(isolated_cwd):

    (motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions").mkdir(
        parents=True
    )

    with patch("shutil.which", return_value="/usr/bin/node"):
        with pytest.raises(FileNotFoundError, match="does-not-exist"):
            motion_graphics.render_composition(
                "does-not-exist",
                {},
                Path("out.webm"),
            )


def test_render_composition_builds_correct_command(isolated_cwd):

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "lower-third.html").write_text("<html></html>")

    def fake_run(command, cwd, capture_output, text, timeout, stdin=None, env=None):
        # simulate the render actually producing the output file,
        # like the real CLI would
        output_path = Path(command[command.index("--output") + 1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake webm bytes")
        return _fake_completed_process(returncode=0)

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch("subprocess.run", side_effect=fake_run) as mock_run:

        output = motion_graphics.render_composition(
            "lower-third",
            {"name": "Adam", "title": "NexaSec"},
            Path("projects/lesson-001/assets/graphics/lower-thirds/1.1.webm"),
        )

    assert output.exists()

    call_args = mock_run.call_args
    command = call_args.args[0]

    assert command[0:4] == ["npx", "--yes", "hyperframes", "render"]
    assert "--composition" in command
    assert command[command.index("--composition") + 1] == str(
        Path("compositions") / "lower-third.html"
    )
    assert "--variables" in command
    assert "--format" in command
    assert command[command.index("--format") + 1] == "webm"
    assert "--strict-variables" in command
    assert call_args.kwargs["cwd"] == str(motion_graphics.HYPERFRAMES_PROJECT_DIR)


def test_render_composition_variables_are_valid_json(isolated_cwd):

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "lower-third.html").write_text("<html></html>")

    captured = {}

    def fake_run(command, cwd, capture_output, text, timeout, stdin=None, env=None):
        captured["variables_json"] = command[command.index("--variables") + 1]
        output_path = Path(command[command.index("--output") + 1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake")
        return _fake_completed_process(returncode=0)

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch("subprocess.run", side_effect=fake_run):

        motion_graphics.render_composition(
            "lower-third",
            {"name": "O'Brien \"Loop\" Test", "title": "Edge/Case"},
            Path("out.webm"),
        )

    import json
    parsed = json.loads(captured["variables_json"])
    assert parsed["name"] == "O'Brien \"Loop\" Test"
    assert parsed["title"] == "Edge/Case"


def test_render_composition_raises_on_nonzero_exit(isolated_cwd):

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "lower-third.html").write_text("<html></html>")

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch(
             "subprocess.run",
             return_value=_fake_completed_process(
                 returncode=1, stderr="some render error"
             ),
         ):

        with pytest.raises(RuntimeError, match="some render error"):
            motion_graphics.render_composition(
                "lower-third",
                {},
                Path("out.webm"),
            )


def test_render_composition_raises_if_output_missing_despite_success(isolated_cwd):

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "lower-third.html").write_text("<html></html>")

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch(
             "subprocess.run",
             return_value=_fake_completed_process(returncode=0),
         ):

        with pytest.raises(RuntimeError, match="no output file"):
            motion_graphics.render_composition(
                "lower-third",
                {},
                Path("out.webm"),
            )


def test_render_composition_never_inherits_stdin(isolated_cwd):
    """
    Regression test: a subprocess that inherits stdin can hang
    forever waiting on a prompt it has no way to answer. stdin must
    always be explicitly closed.
    """

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "lower-third.html").write_text("<html></html>")

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch("subprocess.run", side_effect=_fake_run_writes_output) as mock_run:

        motion_graphics.render_composition("lower-third", {}, Path("out.webm"))

    assert mock_run.call_args.kwargs["stdin"] == subprocess.DEVNULL


def test_render_composition_suppresses_telemetry_and_update_check(isolated_cwd):

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "lower-third.html").write_text("<html></html>")

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch("subprocess.run", side_effect=_fake_run_writes_output) as mock_run:

        motion_graphics.render_composition("lower-third", {}, Path("out.webm"))

    env = mock_run.call_args.kwargs["env"]
    assert env["HYPERFRAMES_NO_TELEMETRY"] == "1"
    assert env["HYPERFRAMES_NO_UPDATE_CHECK"] == "1"


def test_build_lower_third_output_path(isolated_cwd):

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "lower-third.html").write_text("<html></html>")

    def fake_run(command, cwd, capture_output, text, timeout, stdin=None, env=None):
        output_path = Path(command[command.index("--output") + 1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake")
        return _fake_completed_process(returncode=0)

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch("subprocess.run", side_effect=fake_run):

        output = motion_graphics.build_lower_third(
            "lesson-001", "1.1", "Adam Chikh", "NexaSec"
        )

    expected = (
        Path("projects") / "lesson-001" / "assets" / "graphics"
        / "lower-thirds" / "1.1.webm"
    )
    assert output == expected.resolve()


def _fake_run_writes_output(command, cwd, capture_output, text, timeout, stdin=None, env=None):
    output_path = Path(command[command.index("--output") + 1])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(b"fake")
    return _fake_completed_process(returncode=0)


def test_build_chapter_card_output_path_and_format(isolated_cwd):

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "chapter-card.html").write_text("<html></html>")

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch("subprocess.run", side_effect=_fake_run_writes_output) as mock_run:

        output = motion_graphics.build_chapter_card(
            "lesson-001", "ch1", "Variables", chapter_number="01"
        )

    expected = (
        Path("projects") / "lesson-001" / "assets" / "graphics"
        / "chapter-cards" / "ch1.webm"
    )
    assert output == expected.resolve()

    command = mock_run.call_args.args[0]
    assert command[command.index("--format") + 1] == "webm"

    import json
    variables = json.loads(command[command.index("--variables") + 1])
    assert variables["chapterTitle"] == "Variables"
    assert variables["chapterNumber"] == "01"


def test_build_intro_is_opaque_mp4(isolated_cwd):

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "intro.html").write_text("<html></html>")

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch("subprocess.run", side_effect=_fake_run_writes_output) as mock_run:

        output = motion_graphics.build_intro("lesson-001", subtitle="Python from Zero")

    expected = Path("projects") / "lesson-001" / "assets" / "graphics" / "intro.mp4"
    assert output == expected.resolve()

    command = mock_run.call_args.args[0]
    assert command[command.index("--format") + 1] == "mp4"


def test_build_outro_is_opaque_mp4(isolated_cwd):

    comp_dir = motion_graphics.HYPERFRAMES_PROJECT_DIR / "compositions"
    comp_dir.mkdir(parents=True)
    (comp_dir / "outro.html").write_text("<html></html>")

    with patch("shutil.which", return_value="/usr/bin/node"), \
         patch("subprocess.run", side_effect=_fake_run_writes_output) as mock_run:

        output = motion_graphics.build_outro("lesson-001")

    expected = Path("projects") / "lesson-001" / "assets" / "graphics" / "outro.mp4"
    assert output == expected.resolve()

    command = mock_run.call_args.args[0]
    assert command[command.index("--format") + 1] == "mp4"
