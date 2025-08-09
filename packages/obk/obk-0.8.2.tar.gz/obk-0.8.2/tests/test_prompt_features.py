import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import obk.cli as cli
from obk.validation import validate_all as _validate_all

PYTHON = sys.executable
REPO_ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(REPO_ROOT / "src")


def _run(args, cwd):
    return subprocess.run(
        [PYTHON, "-m", "obk", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=ENV,
    )


def _write_prompt(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------- reusable XML -------------------------------------------
VALID_PROMPT = (
    "<?xml version='1.0' encoding='UTF-8'?>\n"
    "<gsl-prompt id='20250731T000000+0000'>\n"
    "  <gsl-header>h</gsl-header>\n"
    "  <gsl-block>\n"
    "    <gsl-purpose>p</gsl-purpose>\n"
    "    <gsl-inputs><gsl-value>i</gsl-value></gsl-inputs>\n"
    "    <gsl-outputs><gsl-value>o</gsl-value></gsl-outputs>\n"
    "    <gsl-workflows><gsl-value>w</gsl-value></gsl-workflows>\n"
    "    <gsl-tdd><gsl-test id='T1'>t</gsl-test></gsl-tdd>\n"
    "    <gsl-document-spec><gsl-value>d</gsl-value></gsl-document-spec>\n"
    "  </gsl-block>\n"
    "</gsl-prompt>\n"
)

BROKEN_PROMPT = "<broken>"


# ---------------- tests ---------------------------------------------------
# def test_validate_all(tmp_path, validate_all):
#     _write_prompt(tmp_path / "prompt1.md", VALID_PROMPT)
#
#     errors, passed, failed = validate_all(tmp_path)
#     assert not errors
#     assert passed == 1
#     assert failed == 0


def test_harmonize_all_and_dry_run(tmp_path):
    prompts = tmp_path / "prompts"
    prompt = prompts / "harm.md"
    content = (
        "<gsl-prompt id='20250731T000000+0000'>\n"
        "  <gsl-header>h</gsl-header>\n"
        "  <gsl-block>\n    <gsl-purpose>p</gsl-purpose>\n  </gsl-block>\n"
        "</gsl-prompt>\n"
    )
    _write_prompt(prompt, content)

    assert _run(["harmonize-all", "--prompts-dir", str(prompts)], cwd=tmp_path).returncode == 0
    txt = prompt.read_text()
    assert txt.splitlines()[1].startswith("<gsl-header>")

    _write_prompt(prompt, content)
    dry = _run(["harmonize-all", "--prompts-dir", str(prompts), "--dry-run"], cwd=tmp_path)
    assert dry.returncode == 0
    assert "Would" in dry.stdout
    assert prompt.read_text() == content


# def test_commands_any_directory_with_paths(tmp_path):
#     prompts = tmp_path / "prompts"
#     _write_prompt(prompts / "file.md", VALID_PROMPT)
#     sub = tmp_path / "subdir"
#     sub.mkdir()
#
#     assert _run(["validate-all", "--prompts-dir", str(prompts)], cwd=sub).returncode == 0
#     assert _run(["harmonize-all", "--prompts-dir", str(prompts)], cwd=sub).returncode == 0
#     r3 = _run(["trace-id"], cwd=sub)
#     assert r3.returncode == 0
#     assert re.match(r"\d{8}T\d{6}[+-]\d{4}", r3.stdout.strip())


def test_trace_id_timezones(tmp_path):
    assert re.match(r"\d{8}T\d{6}[+-]\d{4}", _run(
        ["trace-id", "--timezone", "America/New_York"], cwd=tmp_path).stdout.strip())

    bad = _run(["trace-id", "--timezone", "Invalid/Zone"], cwd=tmp_path)
    assert bad.returncode != 0
    text = (bad.stderr + bad.stdout).lower()
    assert "error" in text or "fatal" in text


# ------------- helpers for “today” tests ---------------------------------
def _patch_repo_root(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
    return cli.get_default_prompts_dir()


# def test_validate_today(monkeypatch, capsys, tmp_path):
#     prompts_dir = _patch_repo_root(tmp_path, monkeypatch)
#     prompts_dir.mkdir(parents=True)
#
#     cli_obj = cli.ObkCLI()
#     with pytest.raises(SystemExit) as exc:
#         cli_obj.run(["validate-today"])
#     assert exc.value.code == 0
#
#     _write_prompt(prompts_dir / "bad.md", BROKEN_PROMPT)
#     with pytest.raises(SystemExit):
#         cli_obj.run(["validate-today"])
#
#     (prompts_dir / "bad.md").unlink()
#     _write_prompt(prompts_dir / "good.md", VALID_PROMPT)
#     with pytest.raises(SystemExit) as exc:
#         cli_obj.run(["validate-today"])
#     assert exc.value.code == 0


def test_harmonize_today(monkeypatch, capsys, tmp_path):
    prompts_dir = _patch_repo_root(tmp_path, monkeypatch)
    prompts_dir.mkdir(parents=True)

    file = prompts_dir / "harm.md"
    _write_prompt(
        file,
        "<gsl-prompt id='20250731T000000+0000'><gsl-header>h</gsl-header>"
        "<gsl-block><gsl-purpose>p</gsl-purpose></gsl-block></gsl-prompt>",
    )

    cli_obj = cli.ObkCLI()
    with pytest.raises(SystemExit):
        cli_obj.run(["harmonize-today"])

    _write_prompt(file, file.read_text())  # reset
    with pytest.raises(SystemExit):
        cli_obj.run(["harmonize-today", "--dry-run"])


def test_exit_codes_prompts_not_found(tmp_path):
    assert _run(["validate-all"], cwd=tmp_path).returncode == 2
    assert _run(["harmonize-all"], cwd=tmp_path).returncode == 2


# def test_autolocate_prompts_from_subdir(tmp_path):
#     prompts = tmp_path / "prompts"
#     _write_prompt(prompts / "good.md", VALID_PROMPT)
#     sub = tmp_path / "sub" / "inner"
#     sub.mkdir(parents=True)
#
#     assert _run(["validate-all"], cwd=sub).returncode == 0
#     assert _run(["harmonize-all"], cwd=sub).returncode == 0


def test_summary_no_prompts(monkeypatch, capsys, tmp_path):
    prompts_dir = _patch_repo_root(tmp_path, monkeypatch)
    prompts_dir.mkdir(parents=True)

    cli_obj = cli.ObkCLI()
    with pytest.raises(SystemExit):
        cli_obj.run(["harmonize-today"])
    captured = capsys.readouterr()
    assert "No prompt files found" in captured.out


def test_harmonize_all_dry_run_summary(tmp_path):
    prompts = tmp_path / "prompts"
    file = prompts / "harm.md"
    _write_prompt(
        file,
        "<gsl-prompt id='20250731T000000+0000'><gsl-header>h</gsl-header>"
        "<gsl-block><gsl-purpose>p</gsl-purpose></gsl-block></gsl-prompt>",
    )

    res = _run(["harmonize-all", "--prompts-dir", str(prompts), "--dry-run"], cwd=tmp_path)
    assert res.returncode == 0
    assert "Dry run" in res.stdout
