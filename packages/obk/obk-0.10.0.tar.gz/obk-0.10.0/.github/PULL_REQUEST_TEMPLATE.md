
# feat: `obk generate prompt` (+ alias)

## What
- Add `generate` group with `prompt` command (alias: `generate-prompt`)
- Deterministic UTC pathing:
  - `prompts/YYYY/MM/DD/<TRACE_ID>.xml`
  - `tasks/YYYY/MM/DD/<TRACE_ID>/`
- Packaged programmatic template `src/obk/templates/prompt.xml`
- Tests for default/date/id/collision/force/dry-run/print-paths/root-unset
- Wheel includes for templates (pyproject updated)

## Why
- Eliminate manual prompt scaffolding
- Keep prompts/tasks collocated by UTC + id
- Ensure consistency offline and across platforms

## How (key details)
- Reuse `resolve_project_root()` and `generate_trace_id("UTC")`
- Template loaded via `importlib.resources`
- Write UTF-8 + LF
- Strict ID validation: `^\d{8}T\d{6}[+-]\d{4}$`

## Test plan
- [ ] `pytest -q` passes locally
- [ ] Offline run (choose one):
  - Linux: `bash scripts/offline/install-linux.sh && bash scripts/offline/run-tests.sh`
  - Windows: `pwsh scripts/offline/install.ps1 -Platform win && pwsh scripts/offline/run-tests.ps1`
- [ ] Default generation creates matching file/folder; XML id matches
- [ ] `--date` places under the correct UTC folder
- [ ] `--id` pins the id for file+folder and XML
- [ ] Collision w/o `--force` errors; with `--force` overwrites
- [ ] `--dry-run` prints, writes nothing
- [ ] `--print-paths` prints abs paths and creates artifacts
- [ ] Root unset fails cleanly (no artifacts)

## Messages (asserted in tests)
- Root missing:
  `❌ No project path configured. Run \`obk set-project-path --here\` or use --path <dir>.`
- Invalid date: `❌ Invalid --date format. Expected YYYY-MM-DD (UTC).`
- Invalid id: `❌ Invalid trace id format: <value>`
- Collision: `❌ Prompt already exists: <path>. Use --force to overwrite.`
- Success:
  - `✅ Created: <abs-prompt-file>`
  - `📂 Ensured: <abs-task-folder>`

## Screenshots / Logs
<!-- Optional: paste sample run output or tree of created paths -->

## Checklist
- [ ] Code formatted (`ruff`, `black` if applicable)
- [ ] New files added to wheel include
- [ ] Help text (`--help`) updated
- [ ] No unrelated changes in this PR