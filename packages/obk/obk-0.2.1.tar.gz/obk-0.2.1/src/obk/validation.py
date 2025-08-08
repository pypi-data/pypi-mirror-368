from pathlib import Path
from typing import List, Tuple

import xml.etree.ElementTree as ET
from importlib.resources import files

import xmlschema

from .preprocess import preprocess_text

GLOBAL_ELEMENTS = {"gsl-label", "gsl-title", "gsl-description", "gsl-value"}


def get_schema_path(schema_name: str) -> Path:
    return files("obk.xsd").joinpath(schema_name)


def detect_prompt_type(file_path: Path) -> str:
    name = file_path.stem.lower()
    if "surgery" in name:
        return "surgery"
    return "gsl"


def validate_all(prompts_dir: Path) -> Tuple[List[str], int, int]:
    """Validate all prompts under ``prompts_dir`` using mapped schemas."""

    errors: List[str] = []
    count_passed = 0
    count_failed = 0

    prompts_dir = prompts_dir.resolve()

    for file_path in prompts_dir.rglob("*.md"):
        text = file_path.read_text(encoding="utf-8")
        processed, _ = preprocess_text(text)
        prompt_type = detect_prompt_type(file_path)
        schema_name = "prompt.xsd"
        schema_path = get_schema_path(schema_name)
        schema = xmlschema.XMLSchema(str(schema_path))
        try:
            file_errors = [
                err.reason or str(err) for err in schema.iter_errors(processed)
            ]
        except xmlschema.XMLSchemaException as exc:
            file_errors = [str(exc)]

        if not file_errors:
            root = ET.fromstring(processed)

            def _recurse(elem: ET.Element) -> None:
                seen = []
                for i, child in enumerate(list(elem)):
                    tag = child.tag
                    if tag in GLOBAL_ELEMENTS:
                        if tag in seen:
                            file_errors.append(
                                f"{file_path}: <{elem.tag}> has duplicate <{tag}>"
                            )
                        if any(c.tag not in GLOBAL_ELEMENTS for c in list(elem)[:i]):
                            file_errors.append(
                                f"{file_path}: <{tag}> must appear before other children in <{elem.tag}>"
                            )
                        seen.append(tag)
                    else:
                        if any(c.tag in GLOBAL_ELEMENTS for c in list(elem)[i + 1 :]):
                            file_errors.append(
                                f"{file_path}: global elements must precede other children in <{elem.tag}>"
                            )
                        break
                for child in elem:
                    _recurse(child)

            _recurse(root)

        if file_errors:
            for msg in file_errors:
                errors.append(f"{file_path}: {msg}")
            count_failed += 1
        else:
            count_passed += 1

    return errors, count_passed, count_failed
