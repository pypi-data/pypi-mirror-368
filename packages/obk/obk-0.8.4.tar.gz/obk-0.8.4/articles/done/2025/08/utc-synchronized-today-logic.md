# How to Integrate UTC-Synchronized “Today” Folder Logic into `obk`

This article shows how to upgrade the `obk` CLI so that **`harmonize-today`** and **`validate-today`** always look in the same `/YYYY/MM/DD/` folder as used by the `trace-id` command—**defaulting to UTC, but allowing user override via CLI option**.

The goal is to ensure:

* The “today” folder and the trace ID always refer to the same day, regardless of the machine’s local time zone.
    
* Users (and automation) can explicitly choose a timezone if desired.
    

* * *

## 1. **Overview of the Change**

**Current state:**

* `harmonize-today` and `validate-today` use the system’s local time.
    
* `trace-id` uses UTC by default (with optional override).
    

**Desired state:**

* All three commands (and any others relying on “today”) should use the same timezone logic (default: UTC), configurable via the CLI.
    

* * *

## 2. **Update Folder Calculation**

### a. Refactor the Folder Logic

Open `cli.py` and update the folder selection logic to accept a timezone argument.  
_This will ensure that the “today” folder is calculated exactly as the trace ID, using the same timezone-aware approach._

**Replace your old `get_default_prompts_dir()` with:**

```python
from zoneinfo import ZoneInfo

def get_default_prompts_dir(timezone: str = "UTC"):
    now = datetime.now(ZoneInfo("UTC")).astimezone(ZoneInfo(timezone))
    return (
        REPO_ROOT
        / "prompts"
        / f"{now.year:04}"
        / f"{now.month:02}"
        / f"{now.day:02}"
    )
```

* * *

## 3. **Add Timezone Options to CLI Commands**

### a. Add the `--timezone` CLI option to `harmonize-today` and `validate-today`

Use Typer’s `Option` to add a `--timezone` flag (default: `"UTC"`).

**For `validate-today`:**

```python
def _cmd_validate_today(
    self,
    schema_path: Path = Path(__file__).resolve().parent / "xsd" / "prompt.xsd",
    timezone: str = typer.Option(
        "UTC", "--timezone", "-tz", help="Timezone for 'today' prompt folder (default: UTC)"
    ),
) -> None:
    prompts_dir = get_default_prompts_dir(timezone)
    typer.echo(f"Validating today's prompts under: {prompts_dir.resolve()} (timezone: {timezone})")
    errors, passed, failed = validate_all(prompts_dir, schema_path)
    # ... rest of function unchanged ...
```

**For `harmonize-today`:**

```python
def _cmd_harmonize_today(
    self,
    dry_run: bool = typer.Option(False, help="Show changes without saving"),
    timezone: str = typer.Option(
        "UTC", "--timezone", "-tz", help="Timezone for 'today' prompt folder (default: UTC)"
    ),
) -> None:
    prompts_dir = get_default_prompts_dir(timezone)
    typer.echo(f"Harmonizing TODAY's prompts under: {prompts_dir.resolve()} (timezone: {timezone})")
    # ... rest of function unchanged ...
```

* This lets users run, for example:  
    `obk validate-today --timezone America/New_York`
    

* * *

## 4. **Test and Document the Change**

### a. **Testing**

After patching, run:

```sh
obk trace-id
obk validate-today
obk harmonize-today
```

All should agree on the date folder, and accept `--timezone` for overrides.

### b. **Help Output**

Check:

```sh
obk validate-today --help
obk harmonize-today --help
```

You should see the `--timezone` option and clear documentation.

* * *

## 5. **(Optional) Refactor for DRYness**

If more commands rely on “today,” consider making the timezone option a reusable Typer callback or utility.

* * *

## 6. **Full Source Example (Diff Style)**

Below is a **full code snippet** representing a patch for `cli.py` only (all changes in one place):

```python
# --- imports ---
from zoneinfo import ZoneInfo
import typer
from datetime import datetime

# --- refactored function ---
def get_default_prompts_dir(timezone: str = "UTC"):
    now = datetime.now(ZoneInfo("UTC")).astimezone(ZoneInfo(timezone))
    return (
        REPO_ROOT
        / "prompts"
        / f"{now.year:04}"
        / f"{now.month:02}"
        / f"{now.day:02}"
    )

# --- in ObkCLI.__init__(), update command signatures to accept timezone ---
self.app.command(
    name="validate-today",
    help="Validate today's prompt files only",
    short_help="Validate today's prompts",
)(self._cmd_validate_today)

self.app.command(
    name="harmonize-today",
    help="Harmonize today's prompt files only",
    short_help="Harmonize today's prompts",
)(self._cmd_harmonize_today)

# --- update command methods ---

def _cmd_validate_today(
    self,
    schema_path: Path = Path(__file__).resolve().parent / "xsd" / "prompt.xsd",
    timezone: str = typer.Option(
        "UTC", "--timezone", "-tz", help="Timezone for 'today' prompt folder (default: UTC)"
    ),
) -> None:
    prompts_dir = get_default_prompts_dir(timezone)
    typer.echo(f"Validating today's prompts under: {prompts_dir.resolve()} (timezone: {timezone})")
    errors, passed, failed = validate_all(prompts_dir, schema_path)
    # ...rest unchanged...

def _cmd_harmonize_today(
    self,
    dry_run: bool = typer.Option(False, help="Show changes without saving"),
    timezone: str = typer.Option(
        "UTC", "--timezone", "-tz", help="Timezone for 'today' prompt folder (default: UTC)"
    ),
) -> None:
    prompts_dir = get_default_prompts_dir(timezone)
    typer.echo(f"Harmonizing TODAY's prompts under: {prompts_dir.resolve()} (timezone: {timezone})")
    # ...rest unchanged...
```

* * *

## 7. **Summary Table**

| Command | Folder/ID Date Basis | CLI Option? |
| --- | --- | --- |
| `trace-id` | UTC (or custom timezone) | `--timezone` |
| `validate-today` | UTC (or custom timezone) | `--timezone` |
| `harmonize-today` | UTC (or custom timezone) | `--timezone` |

* * *

## 8. **Conclusion**

By following these steps and code snippets, your `obk` CLI will consistently interpret “today” in the same way everywhere—**defaulting to UTC, but fully user-configurable.** This makes behavior predictable, CI-friendly, and consistent for global teams.

**Pro tip:**  
If you want to ensure even more uniformity, you can consider using the same default/option pattern for any other “date-sensitive” features in your CLI or automation.

* * *