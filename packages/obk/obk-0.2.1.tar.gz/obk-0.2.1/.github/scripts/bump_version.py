# .github/scripts/bump_version.py

import os
import re
import sys
from pathlib import Path

COMMIT_MSG = os.environ.get("GITHUB_COMMIT_MESSAGE", "")

has_minor = "[minor]" in COMMIT_MSG
has_patch = "[patch]" in COMMIT_MSG
has_major = "[major]" in COMMIT_MSG

if has_major:
    print("Skipping deploy: [major] releases are not supported in pre-1.0.0 pipeline.")
    sys.exit(0)

if has_minor and has_patch:
    print("ERROR: Both [minor] and [patch] present in commit message. Refusing to deploy.", file=sys.stderr)
    sys.exit(1)
elif not has_minor and not has_patch:
    print("No [minor] or [patch] found in commit message. Skipping version bump and deploy.")
    sys.exit(0)

pyproject = Path("pyproject.toml")
content = pyproject.read_text(encoding="utf-8")
match = re.search(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
if not match:
    raise SystemExit("Could not find version string in pyproject.toml!")

major, minor, patch = map(int, match.groups())

if has_minor:
    minor += 1
    patch = 0
    action = "minor"
elif has_patch:
    patch += 1
    action = "patch"

new_version = f'{major}.{minor}.{patch}'
new_content = re.sub(
    r'version\s*=\s*"\d+\.\d+\.\d+"',
    f'version = "{new_version}"',
    content
)
pyproject.write_text(new_content, encoding="utf-8")
print(f"Bumped {action} version to {new_version}")
