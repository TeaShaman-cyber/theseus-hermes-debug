import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEV_CHECK = ROOT / "tools" / "dev" / "check"


def run(*args, cwd=None):
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class DevCheckTests(unittest.TestCase):
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
