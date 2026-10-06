"""
Эмулятор оболочки. Этап 4: рабочие команды ls, cd, cat, tac.
"""

import sys
import json
import tkinter as tk

VFS_NAME = "myVFS"


#аргументы

def parse_args(argv):
    """Разбирает аргументы вида vfs=... и script=... ."""
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


#VFS

def make_default_vfs():
    """VFS по умолчанию — если путь не указан или загрузка не удалась."""
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
    """Читает VFS из JSON-файла. Возвращает (vfs, ошибка)."""
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
    """Ищет файл motd в корне VFS. Возвращает строку или None."""
    root = vfs["root"]
    children = root.get("children", {})

    if "motd" in children:
        node = children["motd"]
        if node.get("type") == "file":
            return node.get("content", "")

    return None


#навигация

def split_path(path):
    """
    Разбирает путь на список непустых частей.

    Пример:
      "/home/user"   -> ["home", "user"]
      "home//user/"  -> ["home", "user"]
      ""             -> []
    """
    parts = []
    for part in path.split("/"):
        if part and part != ".":
            parts.append(part)
    return parts


def get_node(vfs, cwd, path):
    """
    Находит узел в VFS по пути.

    vfs — дерево VFS
    cwd — текущая директория (список частей, например ["home", "user"])
    path — путь (строка). Может быть:
        ""            — вернуть узел cwd
        "/"           — корень
        "/etc"        — абсолютный путь от корня
        "docs"        — относительный путь от cwd
        ".."          — на уровень вверх
        "../.."       — на два уровня вверх

    Возвращает (узел, новый_cwd, ошибка).
    новый_cwd — только если узел найден.
    """
    # Определяем стартовые части пути
    if path == "":
        parts = list(cwd)                        # остаёмся на месте
    elif path.startswith("/"):
        parts = split_path(path)                 # абсолютный путь от корня
    else:
        parts = list(cwd) + split_path(path)     # относительный путь

    # Идём от корня по частям
    node = vfs["root"]
    result_parts = []

    for part in parts:
        if part == "..":
            # на уровень вверх, но не выше корня
            if result_parts:
                result_parts.pop()
            continue

        # узел должен быть папкой, чтобы в него зайти
        if node.get("type") != "dir":
            return None, None, f"не папка: {'/'.join(result_parts) or '/'}"

        children = node.get("children", {})
        if part not in children:
            full = "/" + "/".join(result_parts + [part])
            return None, None, f"путь не найден: {full}"

        node = children[part]
        result_parts.append(part)

    return node, result_parts, None


#команды VFS

def cmd_ls(vfs, cwd, args):
    """ls — вывести содержимое папки или имя файла."""
    # Берём первый аргумент; если его нет — показываем текущую папку
    path = args[0] if args else ""

    node, _, error = get_node(vfs, cwd, path)
    if error:
        return f"ls: {error}"

    if node.get("type") == "file":
        # как в UNIX: ls file.txt показывает file.txt
        return path

    # node — папка. Собираем имена детей
    children = node.get("children", {})
    if not children:
        return ""                                # пустая папка — пустой вывод

    return "\n".join(sorted(children.keys()))


def cmd_cd(vfs, cwd, args):
    """cd — сменить текущую директорию. Возвращает (текст, новый_cwd)."""
    path = args[0] if args else "/"              # без аргумента — в корень

    node, new_cwd, error = get_node(vfs, cwd, path)
    if error:
        return f"cd: {error}", cwd               # ошибка — cwd не меняем

    if node.get("type") != "dir":
        return f"cd: не папка: {path}", cwd

    return "", new_cwd                            # успех, cwd обновлён


def cmd_cat(vfs, cwd, args):
    """cat — вывести содержимое файла."""
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
    """tac — как cat, но строки в обратном порядке."""
    if not args:
        return "tac: не указан файл"

    path = args[0]
    node, _, error = get_node(vfs, cwd, path)
    if error:
        return f"tac: {error}"

    if node.get("type") != "file":
        return f"tac: это папка: {path}"

    content = node.get("content", "")
    lines = content.split("\n")                   # разбиваем на строки
    lines.reverse()                               # переворачиваем
    return "\n".join(lines)


#окно

class Window:
    """Окно приложения: область вывода + поле ввода."""

    def __init__(self, root, vfs, motd=None, script_path=None):
        self.root = root
        self.vfs = vfs
        self.cwd = []                            # текущая директория (список частей)

        root.title(f"Эмулятор - {VFS_NAME}")
        root.geometry("700x450")
        root.minsize(500, 300)

        # Поле ввода — внизу
        self.entry = tk.Entry(root, font=("Consolas", 12))
        self.entry.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

        # Область вывода — сверху
        self.output = tk.Text(root, font=("Consolas", 11))
        self.output.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        if motd:
            self.print_line(motd)

        self.print_line(f"{VFS_NAME}: введите команду (ls, cd, cat, tac, exit)")

        if script_path:
            run_script(self, script_path)

    #вывод

    def print_line(self, text):
        """Добавляет строку в область вывода. Пустую строку — тоже."""
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    #ввод

    def on_enter(self, event):
        """Обработка Enter в поле ввода."""
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
        Выполняет одну команду. Возвращает текст для вывода.
        Если команда exit — закрывает окно и возвращает None.
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
            return text_out or None              # пустой вывод — не печатаем

        if command == "cat":
            return cmd_cat(self.vfs, self.cwd, args)

        if command == "tac":
            return cmd_tac(self.vfs, self.cwd, args)

        return f"Ошибка: неизвестная команда '{command}'"


#скрипт

def run_script(window, path):
    """Выполняет стартовый скрипт: построчно, с эхо-выводом."""
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

        # Если окно закрыто (exit) — прекращаем выполнение
        if not window.root.winfo_exists():
            return

    window.print_line("--- скрипт завершён ---")


#main

def main():
    """Точка входа: читает аргументы, грузит VFS, открывает окно."""
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