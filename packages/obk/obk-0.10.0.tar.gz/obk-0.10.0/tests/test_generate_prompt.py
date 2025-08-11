from pathlib import Path

from typer.testing import CliRunner

from obk.cli import ObkCLI

runner = CliRunner()

def _count_artifacts(root: Path):
    prompts = list(root.glob("prompts/*/*/*/*.md"))
    tasks = list(root.glob("tasks/*/*/*/*"))
    return prompts, tasks

def test_generate_prompt_default_creates_matching_file_and_folder(tmp_path: Path, monkeypatch):
    # Arrange
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    # Act
    result = runner.invoke(app, ["generate", "prompt"])

    # Assert
    assert result.exit_code == 0, result.output
    prompts, tasks = _count_artifacts(tmp_path)
    assert len(prompts) == 1, f"expected 1 prompt file, got {prompts}"
    assert len(tasks) == 1, f"expected 1 task folder, got {tasks}"

    prompt_file = prompts[0]
    task_folder = tasks[0]
    assert prompt_file.stem == task_folder.name, "file/folder names must match"

    content = prompt_file.read_text(encoding="utf-8")
    assert f'id="{prompt_file.stem}"' in content

def test_generate_prompt_with_date_and_id_exact_paths(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    tid = "20250809T130102+0000"
    result = runner.invoke(app, ["generate", "prompt", "--date", "2025-08-09", "--id", tid])
    assert result.exit_code == 0, result.output

    pf = tmp_path / "prompts" / "2025" / "08" / "09" / f"{tid}.md"
    tf = tmp_path / "tasks" / "2025" / "08" / "09" / tid
    assert pf.exists(), f"missing prompt file: {pf}"
    assert tf.exists(), f"missing task folder: {tf}"
    assert f'id="{tid}"' in pf.read_text(encoding="utf-8")

def test_generate_prompt_collision_without_force_fails(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    tid = "20250809T000000+0000"
    args = ["generate", "prompt", "--date", "2025-08-09", "--id", tid]
    r1 = runner.invoke(app, args)
    assert r1.exit_code == 0, r1.output

    r2 = runner.invoke(app, args)  # same again, no --force
    assert r2.exit_code != 0, "expected non-zero on collision"
    assert "already exists" in r2.output.lower()

def test_generate_prompt_force_overwrites(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    tid = "20250809T000001+0000"
    args = ["generate", "prompt", "--date", "2025-08-09", "--id", tid]
    r1 = runner.invoke(app, args)
    assert r1.exit_code == 0, r1.output

    # Overwrite
    r2 = runner.invoke(app, args + ["--force"])
    assert r2.exit_code == 0, r2.output

def test_generate_prompt_dry_run_writes_nothing(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    r = runner.invoke(app, ["generate", "prompt", "--date", "2025-08-09", "--dry-run"])
    assert r.exit_code == 0, r.output
    prompts, tasks = _count_artifacts(tmp_path)
    assert len(prompts) == 0 and len(tasks) == 0, "dry-run should not write artifacts"

def test_generate_prompt_print_paths_outputs_two_lines(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    tid = "20250809T010203+0000"
    r = runner.invoke(
        app,
        [
            "generate",
            "prompt",
            "--date",
            "2025-08-09",
            "--id",
            tid,
            "--print-paths",
        ],
    )
    assert r.exit_code == 0, r.output

    lines = [ln for ln in r.output.splitlines() if ln.strip()]
    assert len(lines) == 2, f"expected exactly 2 lines, got: {lines}"

    pf = Path(lines[0])
    tf = Path(lines[1])
    assert pf.exists() and tf.exists()
    assert pf.name == f"{tid}.md" and tf.name == tid
    s = str(pf).replace("\\", "/")
    t = str(tf).replace("\\", "/")
    assert "prompts/2025/08/09" in s and "tasks/2025/08/09" in t


def test_generate_prompt_dry_run_print_paths_only_two_lines_and_no_writes(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    r = runner.invoke(
        app,
        [
            "generate",
            "prompt",
            "--date",
            "2025-08-09",
            "--id",
            "20250809T010203+0000",
            "--dry-run",
            "--print-paths",
        ],
    )
    assert r.exit_code == 0, r.output
    lines = [ln for ln in r.output.splitlines() if ln.strip()]
    assert len(lines) == 2

    # Ensure nothing was written
    assert not list(tmp_path.glob("prompts/*/*/*/*.md"))
    assert not list(tmp_path.glob("tasks/*/*/*/*"))

def test_generate_prompt_missing_root_fails(tmp_path: Path, monkeypatch):
    # Ensure env and config are not pointing to a valid project
    monkeypatch.delenv("OBK_PROJECT_PATH", raising=False)
    # isolate home/config to tmp so any user config won't be seen
    monkeypatch.setenv("HOME", str(tmp_path / "fakehome"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "fakehome"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "fakehome" / "AppData" / "Roaming"))
    (tmp_path / "fakehome").mkdir(parents=True, exist_ok=True)

    app = ObkCLI().app
    r = runner.invoke(app, ["generate", "prompt"])
    assert r.exit_code != 0, "expected non-zero when project root is unset/invalid"
    # Accept either message depending on code path:
    assert ("no project path configured" in r.output.lower()) or ("does not exist" in r.output.lower())
