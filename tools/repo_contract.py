from __future__ import annotations

import json
from pathlib import Path


REQUIRED_FILES = (
    "README.md",
    "docs/lifecycle.md",
    "tools/dev/check",
    ".github/workflows/qa.yml",
)

README_REQUIRED = (
    "PARKED / INCOMPLETE",
    "bash tools/dev/check",
    "docs/lifecycle.md",
    "not a declared Theseus research line",
)

LIFECYCLE_REQUIRED = (
    "Research status: PARKED / INCOMPLETE",
    "Registry membership: not declared",
    "bash tools/dev/check",
    "QA PASS != acceptance != merge authority != release authority",
    "Release policy: none",
)


def validate_repo(root: Path) -> list[str]:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    readme_path = root / "README.md"
    if readme_path.is_file():
        readme = readme_path.read_text(encoding="utf-8")
        for token in README_REQUIRED:
            if token not in readme:
                errors.append(f"README missing lifecycle token: {token}")

    lifecycle_path = root / "docs/lifecycle.md"
    if lifecycle_path.is_file():
        lifecycle = lifecycle_path.read_text(encoding="utf-8")
        for token in LIFECYCLE_REQUIRED:
            if token not in lifecycle:
                errors.append(f"lifecycle policy missing token: {token}")

    workflow_path = root / ".github/workflows/qa.yml"
    if workflow_path.is_file():
        workflow = workflow_path.read_text(encoding="utf-8")
        if "bash tools/dev/check" not in workflow:
            errors.append("CI must invoke canonical command: bash tools/dev/check")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_repo(root)
    print(json.dumps({"status": "PASS" if not errors else "INVALID", "errors": errors}, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
