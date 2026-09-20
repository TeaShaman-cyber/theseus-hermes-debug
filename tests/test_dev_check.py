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
        self.assertIn("QA_BASE_MODE", text)
        self.assertIn("github.event.before", text)
        self.assertIn("github.event.pull_request.base.sha", text)
        self.assertIn("direct", text)
        self.assertIn("merge-base", text)

    def test_direct_push_mode_preserves_pre_push_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(0, run("git", "init", "-q", cwd=root).returncode)
            self.assertEqual(0, run("git", "config", "user.name", "test", cwd=root).returncode)
            self.assertEqual(0, run("git", "config", "user.email", "test@example.invalid", cwd=root).returncode)

            target = root / "tracked.txt"
            target.write_text("clean\n", encoding="utf-8")
            run("git", "add", "tracked.txt", cwd=root)
            self.assertEqual(0, run("git", "commit", "-q", "-m", "root", cwd=root).returncode)

            target.write_text("bad trailing whitespace   \n", encoding="utf-8")
            self.assertEqual(0, run("git", "commit", "-q", "-am", "bad", cwd=root).returncode)
            bad = run("git", "rev-parse", "HEAD", cwd=root).stdout.strip()

            target.write_text("bad trailing whitespace\n", encoding="utf-8")
            self.assertEqual(0, run("git", "commit", "-q", "-am", "clean", cwd=root).returncode)
            before = run("git", "rev-parse", "HEAD", cwd=root).stdout.strip()

            self.assertEqual(0, run("git", "checkout", "-q", bad, cwd=root).returncode)
            (root / "other.txt").write_text("new branch work\n", encoding="utf-8")
            run("git", "add", "other.txt", cwd=root)
            self.assertEqual(0, run("git", "commit", "-q", "-m", "replacement", cwd=root).returncode)

            probe = run(
                "bash",
                "-c",
                'source "$1"; cd "$2"; QA_BASE_MODE=direct resolve_qa_diff_base "$3"',
                "bash",
                str(DEV_CHECK),
                str(root),
                before,
            )
            self.assertEqual(0, probe.returncode, probe.stdout + probe.stderr)
            self.assertEqual(before, probe.stdout.strip())
            direct = run("git", "diff", "--check", f"{before}..HEAD", cwd=root)
            self.assertNotEqual(0, direct.returncode)
            self.assertIn("trailing whitespace", direct.stdout + direct.stderr)

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
