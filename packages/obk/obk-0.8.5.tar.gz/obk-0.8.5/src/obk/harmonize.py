import re
from typing import List, Tuple


def harmonize_text(text: str) -> Tuple[str, List[str]]:
    lines = text.splitlines()
    out_lines = []
    in_code_block = False
    actions = []
    opening_tag_regex = re.compile(
        r"<[a-zA-Z0-9_\-]+(\s+[^>]*)?>\s*$"
    )  # matches <tag> or <tag attr="...">
    i = 0
    while i < len(lines):
        line = lines[i]
        out_lines.append(line)
        # toggle code block state
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            i += 1
            continue
        if in_code_block:
            i += 1
            continue

        # check for trailing text on same line after opening tag
        match = re.match(r"^(.*(<[a-zA-Z0-9_\-]+(\s+[^>]*)?>))([^\n<]+.*)$", line)
        if match:
            # split trailing text onto new line + blank after tag
            out_lines[-1] = match.group(2)  # only tag
            out_lines.append("")  # blank line
            out_lines.append(match.group(4).strip())
            actions.append(f"Split and inserted blank after opening tag at line {i+1}")
            i += 1
            continue

        # if line ends with an opening tag, check next line for blank
        if opening_tag_regex.search(line):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() and not next_line.lstrip().startswith("<"):
                    # next line is non-blank and not a tag, so insert blank line
                    out_lines.append("")
                    actions.append(f"Inserted blank after opening tag at line {i+1}")
        i += 1

    result_text = "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")
    return result_text, actions
