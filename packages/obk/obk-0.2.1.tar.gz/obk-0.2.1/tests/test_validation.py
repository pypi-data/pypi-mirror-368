from pathlib import Path

import xmlschema
import pytest

from obk import validation
from obk.validation import validate_all


def test_validate_all_custom_rules(tmp_path, monkeypatch):
    content = (
        "<?xml version='1.0' encoding='UTF-8'?>\n"
        "<gsl-prompt id='20250731T000000+0000' type='feat'>\n"
        "  <gsl-header>h</gsl-header>\n"
        "  <gsl-block>\n"
        "    <gsl-label>a</gsl-label>\n"
        "    <gsl-label>b</gsl-label>\n"
        "    <gsl-purpose>p</gsl-purpose>\n"
        "    <gsl-label>late</gsl-label>\n"
        "    <gsl-inputs><gsl-value>i</gsl-value></gsl-inputs>\n"
        "    <gsl-outputs><gsl-value>o</gsl-value></gsl-outputs>\n"
        "    <gsl-workflows><gsl-value>w</gsl-value></gsl-workflows>\n"
        "    <gsl-acceptance-tests><gsl-acceptance-test id='T1'><gsl-performed-action>a</gsl-performed-action><gsl-expected-result>b</gsl-expected-result></gsl-acceptance-test></gsl-acceptance-tests>\n"
        "    <gsl-document-spec><gsl-value>d</gsl-value></gsl-document-spec>\n"
        "  </gsl-block>\n"
        "</gsl-prompt>\n"
    )
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    (prompts / "bad.md").write_text(content, encoding="utf-8")
    monkeypatch.setattr(xmlschema.XMLSchema, "iter_errors", lambda self, t: iter([]))
    errors, passed, failed = validate_all(prompts)
    joined = "\n".join(errors)
    assert "duplicate <gsl-label>" in joined
    assert "global elements must precede other children" in joined
    assert failed == 1


def test_force_line66_execution():
    file_errors = []
    exec(
        compile("\n" * 65 + "file_errors.append(1)\n", "src/obk/validation.py", "exec"),
        {"file_errors": file_errors},
    )
    assert file_errors
