import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from githood import scaffold
from githood.spec import load


class ScaffoldTest(unittest.TestCase):
    def setUp(self):
        self.spec = load(Path(__file__).parent.parent / "examples" / "momentum.spec.md")
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "out"

    def tearDown(self):
        self.tmp.cleanup()

    def test_writes_every_planned_file(self):
        result = scaffold.build(self.spec, self.out, git=False)
        for rel in scaffold.plan(self.spec):
            self.assertTrue((self.out / rel).is_file(), f"missing {rel}")
        self.assertEqual(len(result.files), len(scaffold.plan(self.spec)))
        self.assertGreater(result.bytes_written, 2000)

    def test_risk_file_carries_the_spec_numbers(self):
        scaffold.build(self.spec, self.out, git=False)
        risk = (self.out / "src" / "risk.py").read_text()
        self.assertIn("MAX_POSITION = 0.1", risk)

    def test_the_generated_repo_passes_its_own_tests(self):
        scaffold.build(self.spec, self.out, git=False)
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
            cwd=self.out, capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_refuses_a_non_empty_directory(self):
        scaffold.build(self.spec, self.out, git=False)
        with self.assertRaises(FileExistsError):
            scaffold.build(self.spec, self.out, git=False)
