"""
Эмулятор оболочки. Этап 5: команды touch и rm (изменение VFS в памяти).
"""

import sys
import json
import tkinter as tk

VFS_NAME = "myVFS"


# ---------------------------------------------------------------- аргументы

def parse_args(argv):
    """
    Разбирает аргументы командной строки.

    Поддерживает:
        vfs=<путь>     — путь к JSON-файлу VFS
        script=<путь>  — путь к стартовому скрипту

    Возвращает кортеж (vfs_path, script_path).
    """
    vfs_path = None
    script_path = None

    for arg in argv:
        if arg.startswith("vfs="):
            vfs_path = arg[4:]
        elif arg.startswith("script="):
            script_path = arg[7:]
        else:
            print(f"Неизвестный аргумент: {arg}")

    return vfs_path, script_path


# ---------------------------------------------------------------- VFS

def make_default_vfs():
    """
    Возвращает VFS по умолчанию.

    Используется, если путь к VFS не указан или загрузка не удалась.
    """
    return {
        "name": "default",
        "root": {
            "type": "dir",
            "children": {
                "readme.txt": {
                    "type": "file",
                    "content": "Это VFS по умолчанию."
                },
                "docs": {
                    "type": "dir",
                    "children": {
                        "info.txt": {
                            "type": "file",
                            "content": "Информация."
                        }
                    }
                }
            }
        }
    }


def load_vfs(path):
    """
    Читает VFS из JSON-файла.

    Возвращает кортеж (vfs, ошибка):
        - при успехе: (словарь VFS, None)
        - при ошибке: (None, строка с описанием ошибки)
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            vfs = json.load(f)
    except FileNotFoundError:
        return None, f"файл не найден: {path}"
    except json.JSONDecodeError as e:
        return None, f"неверный формат JSON: {e}"
    except Exception as e:
        return None, f"ошибка чтения: {e}"

    if "root" not in vfs or "name" not in vfs:
        return None, "в JSON нет полей 'name' или 'root'"

    return vfs, None


def find_motd(vfs):
    """
    Ищет файл motd в корне VFS.

    Возвращает содержимое файла motd, если он есть, иначе None.
    """
    root = vfs["root"]
    children = root.get("children", {})

    if "motd" in children:
        node = children["motd"]
        if node.get("type") == "file":
            return node.get("content", "")

    return None


# ---------------------------------------------------------------- навигация

def split_path(path):
    """
    Разбирает путь на список непустых частей.

    Примеры:
        "/home/user"   -> ["home", "user"]
        "home//user/"  -> ["home", "user"]
        ""             -> []
    """
    parts = []
    for part in path.split("/"):
        if part and part != ".":
            parts.append(part)
    return parts


def split_parent(path):
    """
    Разделяет путь на родительскую папку и имя последнего компонента.

    Примеры:
        "docs/new.txt"    -> ("docs", "new.txt")
        "new.txt"         -> ("", "new.txt")
        "/etc/hostname"   -> ("/etc", "hostname")
        "docs/sub/f.txt"  -> ("docs/sub", "f.txt")

    Возвращает кортеж (родительская_папка, имя).
    """
    parts = split_path(path)
    if not parts:
        return "", ""

    name = parts[-1]
    parent_parts = parts[:-1]
    parent = "/".join(parent_parts)

    # сохраняем абсолютность: если путь был абсолютным — родитель тоже
    if path.startswith("/") and parent:
        parent = "/" + parent

    return parent, name


def get_node(vfs, cwd, path):
    """
    Находит узел в дереве VFS по указанному пути.

    Поддерживает:
        ""       — вернуть узел cwd
        "/"      — корень
        "/etc"   — абсолютный путь
        "docs"   — относительный путь
        ".."     — на уровень вверх

    Возвращает (узел, новый_cwd, ошибка).
    """
    if path == "":
        parts = list(cwd)
    elif path.startswith("/"):
        parts = split_path(path)
    else:
        parts = list(cwd) + split_path(path)

    node = vfs["root"]
    result_parts = []

    for part in parts:
        if part == "..":
            if result_parts:
                result_parts.pop()
            continue

        if node.get("type") != "dir":
            return None, None, f"не папка: {'/'.join(result_parts) or '/'}"

        children = node.get("children", {})
        if part not in children:
            full = "/" + "/".join(result_parts + [part])
            return None, None, f"путь не найден: {full}"

        node = children[part]
        result_parts.append(part)

    return node, result_parts, None


# ---------------------------------------------------------------- команды чтения

def cmd_ls(vfs, cwd, args):
    """
    Команда ls — вывод содержимого папки или имени файла.
    """
    path = args[0] if args else ""

    node, _, error = get_node(vfs, cwd, path)
    if error:
        return f"ls: {error}"

    if node.get("type") == "file":
        return path

    children = node.get("children", {})
    if not children:
        return ""

    return "\n".join(sorted(children.keys()))


def cmd_cd(vfs, cwd, args):
    """
    Команда cd — смена текущей директории.

    Возвращает (текст, новый_cwd).
    """
    path = args[0] if args else "/"

    node, new_cwd, error = get_node(vfs, cwd, path)
    if error:
        return f"cd: {error}", cwd

    if node.get("type") != "dir":
        return f"cd: не папка: {path}", cwd

    return "", new_cwd


def cmd_cat(vfs, cwd, args):
    """
    Команда cat — вывод содержимого файла.
    """
    if not args:
        return "cat: не указан файл"

    path = args[0]
    node, _, error = get_node(vfs, cwd, path)
    if error:
        return f"cat: {error}"

    if node.get("type") != "file":
        return f"cat: это папка: {path}"

    return node.get("content", "")


def cmd_tac(vfs, cwd, args):
    """
    Команда tac — как cat, но строки в обратном порядке.
    """
    if not args:
        return "tac: не указан файл"

    path = args[0]
    node, _, error = get_node(vfs, cwd, path)
    if error:
        return f"tac: {error}"

    if node.get("type") != "file":
        return f"tac: это папка: {path}"

    content = node.get("content", "")
    lines = content.split("\n")
    lines.reverse()
    return "\n".join(lines)


# ---------------------------------------------------------------- команды изменения

def cmd_touch(vfs, cwd, args):
    """
    Команда touch — создаёт пустой файл в VFS (в памяти).

    Правила:
        - если аргумент не указан — ошибка;
        - если родительская папка не существует — ошибка;
        - если родительский узел — не папка — ошибка;
        - если файл с таким именем уже существует — ошибка.

    Изменения касаются только VFS в памяти. JSON-файл на диске
    остаётся неизменным.
    """
    if not args:
        return "touch: не указан файл"

    path = args[0]
    parent_path, name = split_parent(path)

    if not name:
        return f"touch: некорректный путь: {path}"

    parent_node, _, error = get_node(vfs, cwd, parent_path)
    if error:
        return f"touch: {error}"

    if parent_node.get("type") != "dir":
        return f"touch: не папка: {parent_path or '/'}"

    children = parent_node.setdefault("children", {})
    if name in children:
        return f"touch: файл уже существует: {name}"

    children[name] = {"type": "file", "content": ""}
    return ""


def cmd_rm(vfs, cwd, args):
    """
    Команда rm — удаляет файл из VFS (из памяти).

    Правила:
        - если аргумент не указан — ошибка;
        - если родительская папка не существует — ошибка;
        - если файла с таким именем нет — ошибка;
        - если узел — папка — ошибка (удаление папок не поддерживается).

    Изменения касаются только VFS в памяти. JSON-файл на диске
    остаётся неизменным.
    """
    if not args:
        return "rm: не указан файл"

    path = args[0]
    parent_path, name = split_parent(path)

    if not name:
        return f"rm: некорректный путь: {path}"

    parent_node, _, error = get_node(vfs, cwd, parent_path)
    if error:
        return f"rm: {error}"

    if parent_node.get("type") != "dir":
        return f"rm: не папка: {parent_path or '/'}"

    children = parent_node.get("children", {})
    if name not in children:
        full = "/" + "/".join(split_path(parent_path) + [name])
        return f"rm: файл не найден: {full}"

    if children[name].get("type") == "dir":
        return f"rm: это папка, удаление папок не поддерживается: {name}"

    del children[name]
    return ""


# ---------------------------------------------------------------- окно

class Window:
    """
    Окно приложения.

    Отвечает за область вывода, поле ввода и выполнение команд
    в контексте текущей VFS и cwd.
    """

    def __init__(self, root, vfs, motd=None, script_path=None):
        """
        Создаёт окно и все виджеты.

        Параметры:
            root        — корневое окно Tkinter
            vfs         — загруженная VFS (словарь)
            motd        — текст приветствия или None
            script_path — путь к стартовому скрипту или None
        """
        self.root = root
        self.vfs = vfs
        self.cwd = []

        root.title(f"Эмулятор - {VFS_NAME}")
        root.geometry("700x450")
        root.minsize(500, 300)

        self.entry = tk.Entry(root, font=("Consolas", 12))
        self.entry.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

        self.output = tk.Text(root, font=("Consolas", 11))
        self.output.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        if motd:
            self.print_line(motd)

        self.print_line(
            f"{VFS_NAME}: команды: ls, cd, cat, tac, touch, rm, exit"
        )

        if script_path:
            run_script(self, script_path)

    def print_line(self, text):
        """
        Добавляет одну строку в область вывода.
        """
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def on_enter(self, event):
        """
        Обрабатывает нажатие Enter в поле ввода.
        """
        text = self.entry.get()
        self.entry.delete(0, tk.END)

        if not text.strip():
            return

        self.print_line(f"{VFS_NAME}$ {text}")

        result = self.execute(text)
        if result is not None:
            self.print_line(result)

    def execute(self, text):
        """
        Выполняет одну команду.

        Возвращает текст для вывода. Для команд без вывода (например,
        успешный cd) возвращает None, чтобы не печатать пустую строку.
        """
        parts = text.split()
        command = parts[0]
        args = parts[1:]

        if command == "exit":
            self.print_line("exit: завершение работы.")
            self.root.destroy()
            return None

        if command == "ls":
            return cmd_ls(self.vfs, self.cwd, args)

        if command == "cd":
            text_out, new_cwd = cmd_cd(self.vfs, self.cwd, args)
            self.cwd = new_cwd
            return text_out or None

        if command == "cat":
            return cmd_cat(self.vfs, self.cwd, args)

        if command == "tac":
            return cmd_tac(self.vfs, self.cwd, args)

        if command == "touch":
            text_out = cmd_touch(self.vfs, self.cwd, args)
            return text_out or None

        if command == "rm":
            text_out = cmd_rm(self.vfs, self.cwd, args)
            return text_out or None

        return f"Ошибка: неизвестная команда '{command}'"


# ---------------------------------------------------------------- скрипт

def run_script(window, path):
    """
    Выполняет стартовый скрипт построчно.

    Если очередная команда закрыла окно (exit), выполнение прекращается.
    """
    window.print_line(f"--- выполнение скрипта: {path} ---")

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        window.print_line(f"Ошибка: файл скрипта не найден: {path}")
        return

    for raw in lines:
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        window.print_line(f"{VFS_NAME}$ {line}")

        result = window.execute(line)
        if result is not None:
            window.print_line(result)

        if not window.root.winfo_exists():
            return

    window.print_line("--- скрипт завершён ---")


# ---------------------------------------------------------------- main

def main():
    """
    Точка входа приложения.
    """
    vfs_path, script_path = parse_args(sys.argv[1:])

    print(f"VFS: {vfs_path}")
    print(f"Script: {script_path}")

    if vfs_path:
        vfs, error = load_vfs(vfs_path)
        if error:
            print(f"Ошибка загрузки VFS: {error}")
            vfs = make_default_vfs()
            vfs_load_error = f"Ошибка загрузки VFS: {error}"
        else:
            vfs_load_error = None
    else:
        vfs = make_default_vfs()
        vfs_load_error = None

    motd = find_motd(vfs)

    root = tk.Tk()
    window = Window(root, vfs, motd=motd, script_path=script_path)

    if vfs_load_error:
        window.output.insert("1.0", vfs_load_error + "\n")

    root.mainloop()


if __name__ == "__main__":
    main()