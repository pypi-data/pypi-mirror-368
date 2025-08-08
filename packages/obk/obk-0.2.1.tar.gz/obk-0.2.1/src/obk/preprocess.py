import html
import re
from typing import List, Tuple

_CODE_PATTERN = re.compile(r"(?:```.*?```|~~~.*?~~~|`[^`]*`)", re.S)


def preprocess_text(text: str) -> Tuple[str, List[str]]:
    """Return XML-safe text and a list of placeholders."""
    placeholders: List[str] = []

    def _code_repl(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"__GSL_CODE_{len(placeholders) - 1}__"

    text = _CODE_PATTERN.sub(_code_repl, text)

    parts = re.split(r"(<[/?A-Za-z][^>]*>)", text)
    for i, part in enumerate(parts):
        if part.startswith("<") and part.endswith(">"):
            continue
        parts[i] = html.escape(part, quote=True)
    processed = "".join(parts)
    return processed, placeholders


def postprocess_text(text: str, placeholders: List[str]) -> str:
    """Replace placeholders with original code and unescape XML entities."""
    for idx, original in enumerate(placeholders):
        text = text.replace(f"__GSL_CODE_{idx}__", original)
    return html.unescape(text)
