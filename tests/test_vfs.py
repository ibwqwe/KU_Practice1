"""
Простые тесты для логики VFS.

Запускаются через unittest — стандартную библиотеку Python.
"""

import sys
import os
import unittest

# Добавляем src в путь, чтобы импортировать main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import main


class TestSplitPath(unittest.TestCase):
    """Тесты функции split_path."""

    def test_simple(self):
        """Простой путь разбивается на части."""
        self.assertEqual(main.split_path("/home/user"), ["home", "user"])

    def test_double_slash(self):
        """Двойной слэш игнорируется."""
        self.assertEqual(main.split_path("home//user"), ["home", "user"])

    def test_empty(self):
        """Пустой путь даёт пустой список."""
        self.assertEqual(main.split_path(""), [])

    def test_dot(self):
        """Точка игнорируется."""
        self.assertEqual(main.split_path("./home"), ["home"])


class TestLs(unittest.TestCase):
    """Тесты команды ls."""

    def setUp(self):
        """Готовим VFS по умолчанию перед каждым тестом."""
        self.vfs = main.make_default_vfs()

    def test_ls_root(self):
        """ls в корне показывает файлы и папки."""
        result = main.cmd_ls(self.vfs, [], [])
        # В VFS по умолчанию: readme.txt и docs
        self.assertIn("readme.txt", result)
        self.assertIn("docs", result)

    def test_ls_file(self):
        """ls на файл показывает его имя."""
        result = main.cmd_ls(self.vfs, [], ["readme.txt"])
        self.assertEqual(result, "readme.txt")

    def test_ls_missing(self):
        """ls несуществующего пути даёт ошибку."""
        result = main.cmd_ls(self.vfs, [], ["nope"])
        self.assertTrue(result.startswith("ls:"))


class TestCd(unittest.TestCase):
    """Тесты команды cd."""

    def setUp(self):
        self.vfs = main.make_default_vfs()

    def test_cd_root(self):
        """cd без аргументов переходит в корень."""
        text, cwd = main.cmd_cd(self.vfs, ["docs"], [])
        self.assertEqual(cwd, [])

    def test_cd_into_dir(self):
        """cd в существующую папку."""
        text, cwd = main.cmd_cd(self.vfs, [], ["docs"])
        self.assertEqual(cwd, ["docs"])

    def test_cd_missing(self):
        """cd в несуществующую папку — ошибка, cwd не меняется."""
        text, cwd = main.cmd_cd(self.vfs, [], ["nope"])
        self.assertEqual(cwd, [])
        self.assertTrue(text.startswith("cd:"))

    def test_cd_into_file(self):
        """cd на файл — ошибка."""
        text, cwd = main.cmd_cd(self.vfs, [], ["readme.txt"])
        self.assertTrue(text.startswith("cd:"))


class TestCatTac(unittest.TestCase):
    """Тесты команд cat и tac."""

    def setUp(self):
        self.vfs = main.make_default_vfs()

    def test_cat(self):
        """cat выводит содержимое файла."""
        result = main.cmd_cat(self.vfs, [], ["readme.txt"])
        self.assertIn("VFS", result)

    def test_cat_missing(self):
        """cat несуществующего файла — ошибка."""
        result = main.cmd_cat(self.vfs, [], ["nope"])
        self.assertTrue(result.startswith("cat:"))

    def test_cat_dir(self):
        """cat на папку — ошибка."""
        result = main.cmd_cat(self.vfs, [], ["docs"])
        self.assertTrue(result.startswith("cat:"))

    def test_tac(self):
        """tac переворачивает строки."""
        # В VFS по умолчанию у docs/info.txt одна строка — ничего не перевернётся.
        # Сделаем свой файл с несколькими строками.
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