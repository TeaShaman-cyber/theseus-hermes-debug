import tempfile
import unittest
from pathlib import Path

from tools.repo_contract import validate_repo


VALID_README = """# repo

**PARKED / INCOMPLETE**

This repository is not a declared Theseus research line.
See docs/lifecycle.md.

bash tools/dev/check
"""

VALID_LIFECYCLE = """# lifecycle

Research status: PARKED / INCOMPLETE
Registry membership: not declared
bash tools/dev/check
QA PASS != acceptance != merge authority != release authority
Release policy: none
"""

VALID_WORKFLOW = """steps:
  - run: bash tools/dev/check
"""


def write_fixture(root: Path) -> None:
    (root / "docs").mkdir(parents=True)
    (root / "tools/dev").mkdir(parents=True)
    (root / ".github/workflows").mkdir(parents=True)
    (root / "README.md").write_text(VALID_README, encoding="utf-8")
    (root / "docs/lifecycle.md").write_text(VALID_LIFECYCLE, encoding="utf-8")
    (root / "tools/dev/check").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    (root / ".github/workflows/qa.yml").write_text(VALID_WORKFLOW, encoding="utf-8")


class RepoContractTests(unittest.TestCase):
    def test_valid_fixture_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            self.assertEqual([], validate_repo(root))

    def test_missing_lifecycle_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            (root / "docs/lifecycle.md").unlink()
            self.assertIn(
                "missing required file: docs/lifecycle.md",
                validate_repo(root),
            )

    def test_release_policy_cannot_silently_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            policy = root / "docs/lifecycle.md"
            policy.write_text(
                VALID_LIFECYCLE.replace("Release policy: none", "Release policy: checkpoint"),
                encoding="utf-8",
            )
            self.assertIn(
                "lifecycle policy missing token: Release policy: none",
                validate_repo(root),
            )

    def test_ci_must_call_canonical_qa(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            (root / ".github/workflows/qa.yml").write_text(
                "steps:\n  - run: python3 -m unittest\n",
                encoding="utf-8",
            )
            self.assertIn(
                "CI must invoke canonical command: bash tools/dev/check",
                validate_repo(root),
            )


if __name__ == "__main__":
    unittest.main()
