"""
Simple tests for VFS logic.

Run via unittest - standard Python library.
"""

import sys
import os
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "src")
)
import main


class TestSplitPath(unittest.TestCase):
    """Tests for split_path."""

    def test_simple(self):
        """Simple path is split into parts."""
        self.assertEqual(
            main.split_path("/home/user"),
            ["home", "user"]
        )

    def test_double_slash(self):
        """Double slash is ignored."""
        self.assertEqual(
            main.split_path("home//user"),
            ["home", "user"]
        )

    def test_empty(self):
        """Empty path gives empty list."""
        self.assertEqual(main.split_path(""), [])

    def test_dot(self):
        """Dot is ignored."""
        self.assertEqual(
            main.split_path("./home"),
            ["home"]
        )


class TestLs(unittest.TestCase):
    """Tests for ls command."""

    def setUp(self):
        """Prepare default VFS before each test."""
        self.vfs = main.make_default_vfs()

    def test_ls_root(self):
        """ls in root shows files and dirs."""
        result = main.cmd_ls(self.vfs, [], [])
        self.assertIn("readme.txt", result)
        self.assertIn("docs", result)

    def test_ls_file(self):
        """ls on file shows its name."""
        result = main.cmd_ls(self.vfs, [], ["readme.txt"])
        self.assertEqual(result, "readme.txt")

    def test_ls_missing(self):
        """ls on missing path gives error."""
        result = main.cmd_ls(self.vfs, [], ["nope"])
        self.assertTrue(result.startswith("ls:"))


class TestCd(unittest.TestCase):
    """Tests for cd command."""

    def setUp(self):
        """Prepare default VFS."""
        self.vfs = main.make_default_vfs()

    def test_cd_root(self):
        """cd without args goes to root."""
        text, cwd = main.cmd_cd(self.vfs, ["docs"], [])
        self.assertEqual(cwd, [])

    def test_cd_into_dir(self):
        """cd into existing dir."""
        text, cwd = main.cmd_cd(self.vfs, [], ["docs"])
        self.assertEqual(cwd, ["docs"])

    def test_cd_missing(self):
        """cd into missing dir - error, cwd unchanged."""
        text, cwd = main.cmd_cd(self.vfs, [], ["nope"])
        self.assertEqual(cwd, [])
        self.assertTrue(text.startswith("cd:"))

    def test_cd_into_file(self):
        """cd on file - error."""
        text, cwd = main.cmd_cd(
            self.vfs, [], ["readme.txt"]
        )
        self.assertTrue(text.startswith("cd:"))


class TestCatTac(unittest.TestCase):
    """Tests for cat and tac commands."""

    def setUp(self):
        """Prepare default VFS."""
        self.vfs = main.make_default_vfs()

    def test_cat(self):
        """cat shows file content."""
        result = main.cmd_cat(self.vfs, [], ["readme.txt"])
        self.assertIn("VFS", result)

    def test_cat_missing(self):
        """cat on missing file - error."""
        result = main.cmd_cat(self.vfs, [], ["nope"])
        self.assertTrue(result.startswith("cat:"))

    def test_cat_dir(self):
        """cat on dir - error."""
        result = main.cmd_cat(self.vfs, [], ["docs"])
        self.assertTrue(result.startswith("cat:"))

    def test_tac(self):
        """tac reverses lines."""
        vfs = {
            "name": "t",
            "root": {
                "type": "dir",
                "children": {
                    "f.txt": {
                        "type": "file",
                        "content": "one\ntwo\nthree"
                    }
                }
            }
        }
        result = main.cmd_tac(vfs, [], ["f.txt"])
        self.assertEqual(result, "three\ntwo\none")


if __name__ == "__main__":
    unittest.main()
