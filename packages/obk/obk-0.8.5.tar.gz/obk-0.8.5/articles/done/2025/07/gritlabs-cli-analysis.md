# How to Reproduce Gritlabs Functionality in your own CLI

This repository packages a command line interface that can be invoked simply as
`gritlabs`. The CLI offers commands such as `validate-all` and
`harmonize-all` for validating and formatting prompt files that mix Markdown with
Grit Structured Language (GSL) XML. Below is an overview of how those features
work and how the executable is set up so it can run from any directory.

## Command Implementation

Both `validate-all` and `harmonize-all` are implemented in `gritlabs/cli.py`.
The validation command loads XSD schemas, preprocesses each prompt and reports
schema or harmony errors:

```python
def _cmd_validate_all(args: argparse.Namespace) -> None:
    allowed = _load_template_types()
    schemas = {t: _load_schema(t) for t in allowed}
    inactive = _load_inactive_ids()
    errors = []
    for path in Path("prompts").rglob("*.md"):
        if path.stem in inactive:
            continue
        try:
            _validate_prompt(path, schemas)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: {exc}")
        harmony_issues = find_harmony_issues(path.read_text(encoding="utf-8"))
        for issue in harmony_issues:
            errors.append(f"{path}: {issue}")
    if errors:
        raise ValueError("\\n".join(errors))
```

The harmonize command repairs formatting violations:

```python

def _cmd_harmonize_all(args: argparse.Namespace) -> None:
    allowed = _load_template_types()
    schemas = {t: _load_schema(t) for t in allowed}
    inactive = _load_inactive_ids()
    for path in Path("prompts").rglob("*.md"):
        if path.stem in inactive:
            continue
        # ensure file is valid XML first
        try:
            _validate_prompt(path, schemas)
        except Exception:
            # ignore XML errors; harmonization may help but still attempt
            pass
        original = path.read_text(encoding="utf-8")
        harmonized, actions = harmonize_text(original)
        if not actions:
            continue
        for act in actions:
            prefix = "(Dry-run) " if args.dry_run else "✔️ "
            print(f"{prefix}{act} in {path.name}")
        if not args.dry_run:
            path.write_text(harmonized, encoding="utf-8")
```

## Preprocessing and Postprocessing

Prompt files first go through `preprocess_text`, which preserves code fences and
escapes reserved XML characters. After validation, `postprocess_text` restores
those fences:

```python
    """

    placeholders: List[str] = []

    def _code_repl(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"__GSL_CODE_{len(placeholders) - 1}__"

    # Replace fenced code blocks and inline code with placeholders
    text = _CODE_PATTERN.sub(_code_repl, text)

    parts = re.split(r"(<[/?A-Za-z][^>]*>)", text)
    for i, part in enumerate(parts):
        if part.startswith("<") and part.endswith(">"):
            continue
        parts[i] = html.escape(part, quote=True)
    processed = "".join(parts)
    return processed, placeholders

def postprocess_text(text: str, placeholders: list[str]) -> str:
    """Replace placeholders with their original code block text."""
    for idx, original in enumerate(placeholders):
        text = text.replace(f"__GSL_CODE_{idx}__", original)
    return html.unescape(text)
```

## Command-Line Help

The CLI parser registers every subcommand with a help string. Running
`gritlabs harmonize-all -h` prints usage information thanks to the parser
configuration:

```python
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gritlabs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate")
    gen_sub = gen_parser.add_subparsers(dest="generate_command", required=True)

    trace_parser = gen_sub.add_parser("trace_id", help="Generate a Trace ID")
    trace_parser.add_argument(
        "-t",
        "--timezone",
        default=DEFAULT_TZ,
        help=f"IANA timezone name (default: {DEFAULT_TZ})",
    )
    trace_parser.set_defaults(func=lambda args: print(generate_trace_id(args.timezone)))

    template_parser = subparsers.add_parser("template")
    template_sub = template_parser.add_subparsers(
        dest="template_command", required=True
    )

    gen_template_parser = template_sub.add_parser(
        "generate", help="Generate a prompt from a template"
    )
    gen_template_parser.add_argument("type", help="Template type")
    gen_template_parser.add_argument(
        "-o",
        "--output",
        help="Optional output file path for the generated prompt",
    )
    gen_template_parser.set_defaults(func=_cmd_template_generate)

    ncc_parser = subparsers.add_parser("ncc", help="Manage non-conforming commits")
    ncc_sub = ncc_parser.add_subparsers(dest="ncc_cmd", required=True)

    ncc_add = ncc_sub.add_parser("add", help="Add commit hash")
    ncc_add.add_argument("hash")
    ncc_add.add_argument("-r", "--reason", required=True)
    ncc_add.add_argument("-a", "--author")
    ncc_add.add_argument("-d", "--date")
    ncc_add.set_defaults(func=_cmd_ncc_add)

    ncc_list = ncc_sub.add_parser("list", help="List commits")
    ncc_list.set_defaults(func=_cmd_ncc_list)

    ncc_remove = ncc_sub.add_parser("remove", help="Remove commit by hash")
    ncc_remove.add_argument("hash")
    ncc_remove.set_defaults(func=_cmd_ncc_remove)

    inactive_parser = subparsers.add_parser("inactive", help="Manage inactive prompts")
    inactive_sub = inactive_parser.add_subparsers(dest="inactive_cmd", required=True)

    inactive_add = inactive_sub.add_parser("add", help="Add inactive prompt")
    inactive_add.add_argument("trace_id")
    inactive_add.add_argument("-r", "--reason", required=True)
    inactive_add.set_defaults(func=_cmd_inactive_add)

    inactive_list = inactive_sub.add_parser("list", help="List inactive prompts")
    inactive_list.set_defaults(func=_cmd_inactive_list)

    inactive_remove = inactive_sub.add_parser(
        "remove", help="Remove prompt by Trace ID"
    )
    inactive_remove.add_argument("trace_id")
    inactive_remove.set_defaults(func=_cmd_inactive_remove)

    subparsers.add_parser(
        "validate-all", help="Validate all prompt files"
    ).set_defaults(func=_cmd_validate_all)

    harmonize_parser = subparsers.add_parser(
        "harmonize-all", help="Repair Markdown harmony issues"
    )
    harmonize_parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without modifying files"
    )
    harmonize_parser.set_defaults(func=_cmd_harmonize_all)
```

## Executable Entry Point

The project defines a script entry point so the command can be run as
`gritlabs` from any folder:

```toml
[tool.setuptools]
packages = ["gritlabs"]

[tool.setuptools.package-data]
"gritlabs" = ["data/*.xml", "data/*.xsd", "templates/*.md"]

[project.scripts]
gritlabs = "gritlabs.cli:main"
```

## Running from Any Directory

Unit tests verify the CLI works even when executed from a temporary directory:

```python
def test_cli_portable_resources(tmp_path: Path):
    """CLI should work from any directory and still access packaged resources."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gritlabs.cli",
            "template",
            "generate",
            "feature",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env=env,
    )
    output_path = tmp_path / Path(result.stdout.strip())
    assert output_path.is_file()
```

Following this structure allows you to create your own CLI that validates and
repairs Markdown/XML prompts while being runnable from anywhere.
