from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from file_aggregator.utils import get_file_states, concatenate_file

class TestUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_get_file_states(self) -> None:
        file1 = os.path.join(self.test_dir, "file1.md")
        with open(file1, 'w') as f:
            f.write("test")
        
        states = get_file_states([file1, "nonexistent.md"])
        self.assertIn(file1, states)
        self.assertIsNotNone(states[file1])
        self.assertIsNone(states["nonexistent.md"])

    def test_concatenate_file(self) -> None:
        src1 = os.path.join(self.test_dir, "src1.md")
        src2 = os.path.join(self.test_dir, "src2.md")
        target = os.path.join(self.test_dir, "target.md")

        with open(src1, 'w') as f:
            f.write("# Section 1") # No newline
        with open(src2, 'w') as f:
            f.write("# Section 2\n")

        concatenate_file(target, [src1, src2])

        with open(target, 'r') as f:
            content = f.read()
            # Should have injected a newline between src1 and src2
            self.assertEqual(content, "# Section 1\n# Section 2\n")

    def test_concatenate_file_creates_missing_parent_dirs(self) -> None:
        src = os.path.join(self.test_dir, "src.md")
        nested_target = os.path.join(self.test_dir, "a", "b", "target.md")
        with open(src, "w") as f:
            f.write("ok\n")

        concatenate_file(nested_target, [src])

        self.assertTrue(os.path.isfile(nested_target))
        with open(nested_target, "r") as f:
            self.assertEqual(f.read(), "ok\n")

if __name__ == "__main__":
    unittest.main()
