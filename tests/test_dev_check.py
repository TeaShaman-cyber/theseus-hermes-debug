import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEV_CHECK = ROOT / "tools" / "dev" / "check"
WORKFLOW = ROOT / ".github" / "workflows" / "qa.yml"


def run(*args, cwd=None):
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class DevCheckTests(unittest.TestCase):
    def test_workflow_binds_qa_range_to_event_revisions(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("QA_BASE_REF", text)
        self.assertIn("github.event.before", text)
        self.assertIn("github.event.pull_request.base.sha", text)

    def test_python_syntax_check_does_not_write_bytecode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(0, run("git", "init", "-q", cwd=root).returncode)
            (root / "sample.py").write_text("value = 1\n", encoding="utf-8")
            self.assertEqual(0, run("git", "add", "sample.py", cwd=root).returncode)

            probe = run(
                "bash",
                "-c",
                'source "$1"; cd "$2"; check_python_syntax',
                "bash",
                str(DEV_CHECK),
                str(root),
            )
            self.assertEqual(0, probe.returncode, probe.stdout + probe.stderr)
            self.assertFalse(any(root.rglob("__pycache__")))
            self.assertFalse(any(root.rglob("*.pyc")))

    def test_untracked_embedded_git_directory_is_checked_recursively(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(0, run("git", "init", "-q", cwd=root).returncode)

            vendor = root / "vendor"
            vendor.mkdir()
            self.assertEqual(0, run("git", "init", "-q", cwd=vendor).returncode)
            (vendor / "file.txt").write_text("bad trailing whitespace   \n", encoding="utf-8")

            listed = run(
                "git", "ls-files", "--others", "--exclude-standard", "-z", cwd=root
            )
            self.assertEqual(0, listed.returncode, listed.stderr)
            self.assertIn("vendor/", listed.stdout)

            probe = run(
                "bash",
                "-c",
                'source "$1"; cd "$2"; check_untracked_whitespace',
                "bash",
                str(DEV_CHECK),
                str(root),
            )
            self.assertNotEqual(0, probe.returncode)
            self.assertIn("trailing whitespace", probe.stdout + probe.stderr)

    def test_clean_untracked_embedded_git_directory_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(0, run("git", "init", "-q", cwd=root).returncode)

            vendor = root / "vendor"
            vendor.mkdir()
            self.assertEqual(0, run("git", "init", "-q", cwd=vendor).returncode)
            (vendor / "file.txt").write_text("clean\n", encoding="utf-8")

            probe = run(
                "bash",
                "-c",
                'source "$1"; cd "$2"; check_untracked_whitespace',
                "bash",
                str(DEV_CHECK),
                str(root),
            )
            self.assertEqual(0, probe.returncode, probe.stdout + probe.stderr)


if __name__ == "__main__":
    unittest.main()
