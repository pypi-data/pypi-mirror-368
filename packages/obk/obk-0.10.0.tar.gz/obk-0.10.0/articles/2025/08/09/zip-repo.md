# Cleanly zipping your repo with `git archive` (and adding wheels)

This guide shows a reliable way to produce a **clean zip of only the files you’ve committed**—no caches, no `.git/`, no `node_modules/`—and then (optionally) append build artifacts like `.whl` and `.tar.gz`.

* * *

## Why `git archive`?

* **Respects `.gitignore`** by design: it only includes _tracked_ files.
    
* **Zero setup:** built into Git.
    
* **Repeatable:** same commit → same archive.
    

> You **do not** need a `.zipignore` when using `git archive`.

* * *

## Quick start (Windows, macOS, Linux)

From the repo root:

```bash
# 1) Create a clean zip from the current commit
git archive --format=zip --output obk_clean.zip HEAD
```

That’s it. `obk_clean.zip` now contains exactly what’s committed.

* * *

## Add build artifacts (wheel/sdist)

If you want to include `dist/*.whl` and `dist/*.tar.gz` too:

### Windows (with 7-Zip)

```powershell
git archive --format=zip --output obk_clean.zip HEAD
7z a obk_clean.zip .\dist\*.whl .\dist\*.tar.gz
```

### macOS/Linux (with `zip`)

```bash
git archive --format=zip --output obk_clean.zip HEAD
zip -j obk_clean.zip dist/*.whl dist/*.tar.gz
```

> `-j` strips directory paths when adding files. Omit it if you want to keep `dist/` inside the zip.

* * *

## Include **untracked but not ignored** files (e.g., `prompts/`)

Sometimes you keep data untracked but still want to ship it. Use Git to list both **tracked** and **untracked-but-not-ignored** files, then zip that list.

### Cross-platform approach

```bash
# Build a file list from Git's perspective
git ls-files -co --exclude-standard > filelist.txt

# Use the list to create a zip
# macOS/Linux:
zip -@ obk_clean.zip < filelist.txt

# Windows PowerShell (Compress-Archive):
powershell -Command ^
  "$files = Get-Content filelist.txt; Compress-Archive -Path $files -DestinationPath obk_clean.zip -Force"
```

Then append your wheels as shown above.

> `-c` includes untracked files; `-o` excludes ignored files; `--exclude-standard` respects `.gitignore`, `.git/info/exclude`, and global ignores.

* * *

## Tagging specific versions

Archive a specific tag or commit:

```bash
git archive --format=zip --output obk-0.9.0.zip v0.9.0
# or a branch/commit
git archive --format=zip --output obk-main.zip main
git archive --format=zip --output obk-abc123.zip abc1234
```

* * *

## Verify what’s included

* **macOS/Linux**
    
    ```bash
    unzip -l obk_clean.zip
    ```
    
* **Windows PowerShell**
    
    ```powershell
    $tmp = New-Item -ItemType Directory -Path .\_zipcheck -Force
    Expand-Archive .\obk_clean.zip -DestinationPath $tmp -Force
    Get-ChildItem -Recurse $tmp
    Remove-Item $tmp -Recurse -Force
    ```
    

Check ignore behavior quickly:

```bash
git check-ignore -v -- **/*
```

* * *

## Common pitfalls & fixes

* **Right-click “Send to → Compressed folder” on Windows**  
    Ignores `.gitignore`/`.zipignore`. Use `git archive`, `7z`, or `Compress-Archive` with a file list.
    
* **Submodules not included**  
    `git archive` skips submodule contents. Archive them separately or vendor the needed files.
    
* **You need `dist/` sometimes**  
    Don’t commit `dist/`. Use the “append wheels” step when needed.
    
* **Binary filters or generated files**  
    If a file is generated during build and not tracked, either add it to the `git ls-files -co` flow or append it after.
    

* * *

## Handy scripts

### PowerShell (Windows) — tracked + untracked-not-ignored + wheels

Save as `make-zip.ps1` in your repo root:

```powershell
# Build file list (tracked + untracked-but-not-ignored)
git ls-files -co --exclude-standard > filelist.txt

# Zip those files
$files = Get-Content filelist.txt
Compress-Archive -Path $files -DestinationPath obk_clean.zip -Force

# Append wheels/sdists if present (requires 7-Zip in PATH)
if (Test-Path .\dist) {
  7z a obk_clean.zip .\dist\*.whl .\dist\*.tar.gz | Out-Null
}

Remove-Item filelist.txt -Force
Write-Host "Created obk_clean.zip"
```

### Bash (macOS/Linux) — tracked only + optional wheels

```bash
#!/usr/bin/env bash
set -euo pipefail

# Clean archive from HEAD
git archive --format=zip --output obk_clean.zip HEAD

# Append wheels if present
if compgen -G "dist/*.whl" > /dev/null || compgen -G "dist/*.tar.gz" > /dev/null; then
  zip -j obk_clean.zip dist/*.whl dist/*.tar.gz || true
fi

echo "Created obk_clean.zip"
```

* * *

## CI usage (optional)

In GitHub Actions, produce a clean zip on tag builds:

```yaml
- name: Make clean zip from tag
  run: git archive --format=zip --output obk_${{ github.ref_name }}.zip ${{ github.ref_name }}

- name: Attach wheels to zip (if built)
  if: always()
  run: |
    if ls dist/*.whl >/dev/null 2>&1 || ls dist/*.tar.gz >/dev/null 2>&1; then
      zip -j obk_${{ github.ref_name }}.zip dist/*.whl dist/*.tar.gz || true
    fi
```

* * *

## TL;DR

* Use `git archive` to get a **clean, reproducible** zip of committed files.
    
* If you need extras (e.g., wheels, prompt data), **append them** or build a file list with `git ls-files -co`.
    
* You don’t need `.zipignore`; just keep your `.gitignore` accurate.
    