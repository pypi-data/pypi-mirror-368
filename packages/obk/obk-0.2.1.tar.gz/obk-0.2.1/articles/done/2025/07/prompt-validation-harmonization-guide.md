## How to Add `validate-all`, `harmonize-all`, and `trace-id` Commands to Your CLI

---

### Overview

This guide walks you through adding three essential commands to your Python CLI project:

* **`validate-all`**: Validates prompt (or config) files using an XSD schema.
* **`harmonize-all`**: Auto-corrects formatting or structure in prompt files for consistency and schema compliance.
* **`trace-id`**: Generates a file-safe, timezone-aware trace ID for uniquely naming prompt files and audit records.

All examples are Python-centric, but the same structure can be used in any language or CLI framework.

---

### 1. Directory & Packaging Structure

Recommended layout (inside your Python package):

```
src/
  your_cli/
    __init__.py
    cli.py
    xsd/
      gsl-prompt.xsd
    ...
```

Include the XSD in your package data for portability.

---

### 2. The `validate-all` Command

**Purpose:**
Recursively scan for prompt files (e.g., in a `prompts/` folder), and validate each against your XSD. Report any schema violations.

**Python Example (lxml):**

```python
from lxml import etree
from pathlib import Path

def validate_all_prompts(schema_path, prompts_dir):
    schema_doc = etree.parse(str(schema_path))
    schema = etree.XMLSchema(schema_doc)
    errors = []
    for file_path in Path(prompts_dir).rglob("*.md"):
        try:
            tree = etree.parse(str(file_path))
            schema.assertValid(tree)
        except Exception as e:
            errors.append(f"{file_path}: {e}")
    if errors:
        for error in errors:
            print(error)
        raise SystemExit("Validation failed.")
    print("All prompt files are valid.")
```

*Adapt as needed for your file formats (e.g., Markdown-wrapped XML).*

---

### 3. The `harmonize-all` Command

**Purpose:**
Ensure all prompt files follow a consistent format (e.g., consistent indentation, escaping, section order, etc.). Optionally, auto-fix any deviations.

**Approach:**

* Preprocess files to escape reserved XML characters (see below), while preserving code blocks and inline code with placeholders.
* Parse and pretty-print or rewrite content to match the XSD and project formatting rules.
* Restore any placeholders or special sections after harmonization.

**Example (pseudocode):**

```python
def harmonize_all(prompts_dir):
    for file_path in Path(prompts_dir).rglob("*.md"):
        original = file_path.read_text(encoding="utf-8")
        # 1. Preprocess (escape, handle code blocks)
        processed, placeholders = preprocess_text(original)
        # 2. Reformat or "harmonize" content (see harmonize_text below)
        harmonized, actions = harmonize_text(processed)
        # 3. Postprocess to restore code blocks/inline code
        final = postprocess_text(harmonized, placeholders)
        # 4. Optionally, write back
        file_path.write_text(final, encoding="utf-8")
        for act in actions:
            print(f"✔️ {act} in {file_path.name}")
```

* Add a `--dry-run` flag to print changes without saving them.

---

### 4. The `trace-id` Command

**Purpose:**
Generate a unique, sortable ID with timezone normalization for file naming and traceability.

**Reference Implementation (`get_prompt_id.py`):**

```python
#!/usr/bin/env python3
"""
Generate a file-safe, timezone-normalized Trace ID.
- Default timezone: UTC.
- Use --timezone/-t to specify any IANA timezone.
"""

from datetime import datetime
import argparse

try:
    from zoneinfo import ZoneInfo  # Python ≥3.9
except ImportError:
    from backports.zoneinfo import ZoneInfo

def generate_trace_id(tz_name="UTC"):
    tz = ZoneInfo(tz_name)
    now = datetime.now(ZoneInfo("UTC")).astimezone(tz)
    return now.strftime("%Y%m%dT%H%M%S%z")

def main():
    parser = argparse.ArgumentParser(description="Generate a Trace ID.")
    parser.add_argument("-t", "--timezone", default="UTC", help="IANA timezone name (default: UTC).")
    args = parser.parse_args()
    try:
        trace_id = generate_trace_id(args.timezone)
    except Exception as exc:
        parser.error(f"Invalid timezone '{args.timezone}': {exc}")
    print(trace_id)

if __name__ == "__main__":
    main()
```

* Make this available as a subcommand or separate script in your CLI.

---

### 5. Best Practices

* Keep your schema(s) in a discoverable subfolder (e.g., `xsd/`).
* Validate files early and often—add schema validation to your CI/CD pipeline.
* Run harmonization before validation to auto-correct as many issues as possible.
* Harmonization helps keep your repo clean and contributor-friendly.
* Use the trace ID for all prompt/artifact file naming for easier auditing.
* Collect and report all errors from validation and harmonization, not just the first.

---

### 6. Further Extensions

* Add more schema types later if your CLI grows.
* Support additional harmonization steps as formatting needs evolve.
* Make validation and harmonization fully configurable via CLI flags.

---

## Code Examples and Details

### **Preprocessing Step**

**Escapes XML-reserved characters** everywhere except inside code blocks or inline code (which are replaced with placeholders).

* Inside XML tags (e.g., `<tag ...>`), escaping is **not** applied; only content outside tags is escaped.
* Handles code blocks and inline code by replacing them with placeholders, so their contents are ignored by XML validation.

**Code (`preprocess.py`):**

````python
import html
import re
from typing import List

_CODE_PATTERN = re.compile(r"(?:```.*?```|~~~.*?~~~|`[^`]*`)", re.S)

def preprocess_text(text: str) -> tuple[str, list[str]]:
    """
    Return XML-safe text and a list of placeholders.
    - Code blocks and inline code are replaced with placeholders.
    - All other text (outside XML tags) has XML-reserved characters escaped.
    """
    placeholders: List[str] = []

    def _code_repl(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"__GSL_CODE_{len(placeholders) - 1}__"

    # 1. Replace code with placeholders
    text = _CODE_PATTERN.sub(_code_repl, text)

    # 2. Escape XML characters outside XML tags
    parts = re.split(r"(<[/?A-Za-z][^>]*>)", text)
    for i, part in enumerate(parts):
        if part.startswith("<") and part.endswith(">"):
            continue
        parts[i] = html.escape(part, quote=True)
    processed = "".join(parts)
    return processed, placeholders
````

---

### **Postprocessing Step**

After validation/harmonization, restores code blocks/inline code from the placeholders and **unescapes** any XML entities that were escaped in preprocessing.

**Code (`preprocess.py`):**

```python
def postprocess_text(text: str, placeholders: list[str]) -> str:
    """
    Replace placeholders with original code and unescape XML entities.
    """
    for idx, original in enumerate(placeholders):
        text = text.replace(f"__GSL_CODE_{idx}__", original)
    return html.unescape(text)
```

---

### **Treatment of XML Reserved Characters**

* **Escaping:**
  XML-reserved characters (`<`, `>`, `&`, `"` and `'`) are escaped outside of XML tags and code blocks. (e.g., `&` becomes `&amp;`, `<` becomes `&lt;`)
* **Unescaping:**
  After validation and harmonization, the text is unescaped back to its original form by `html.unescape` in the postprocessing step.

---

### **Typical Workflow**

```python
from preprocess import preprocess_text, postprocess_text

# 1. Read the prompt file
original = prompt_file.read_text(encoding="utf-8")

# 2. Preprocess for XML safety
processed, placeholders = preprocess_text(original)

# 3. Validate XML
import xml.etree.ElementTree as ET
try:
    root = ET.fromstring(processed)
except ET.ParseError as e:
    print(f"Invalid XML: {e}")
    # handle error

# ... further validation (e.g., against XSD) ...

# 4. Postprocess to restore original content
final = postprocess_text(processed, placeholders)
```

---

## **Harmonization**

* **Enforces:**

  * All XML tags must be left-justified (no indentation).
  * Blank line after XML element unless the next line is another tag.
* **Ignores:**

  * Lines within code blocks or inline code.

**Pseudocode (`harmonize.py` logic):**

````python
def harmonize_text(text: str) -> Tuple[str, List[str]]:
    lines = text.splitlines()
    actions: List[str] = []
    i = 0
    in_code = False
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```") or line.lstrip().startswith("~~~"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue
        # Remove indentation from XML tags
        stripped = line.lstrip()
        if stripped.startswith("<") and line != stripped:
            lines[i] = stripped
            actions.append(f"Removed indentation for XML element on line {i + 1}")
        # Insert blank lines after XML elements if needed
        # If the next non-blank line isn't another XML tag, insert a blank
        # ... (simplified for clarity)
        i += 1
    result = "\n".join(lines)
    if text.endswith("\n"):
        result += "\n"
    return result, actions
````

---

## **Summary**

* **Escaping happens everywhere outside tags/code;** code blocks and inline code are untouched.
* **Escaping is reversed (unescaped)** after validation/harmonization so prompt files are human-friendly.
* **All harmonization and validation is performed on preprocessed text.**
* **Restoration/postprocessing brings the file back to its original, user-facing form.**
* **Test all of these steps in your CI to ensure ongoing correctness.**

---

**This approach ensures you get strict XML validation and formatting, without false positives from code/markdown sections—perfect for hybrid prompt files.**
