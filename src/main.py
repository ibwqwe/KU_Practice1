"""
Эмулятор оболочки. Этап 3: загрузка VFS из JSON.
"""

import sys
import json
import tkinter as tk

VFS_NAME = "myVFS"


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

    # Проверяем структуру
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


def run_command(text):
    """Выполняет одну команду. Возвращает (ответ, надо_ли_выйти)."""
    parts = text.split()
    command = parts[0]
    args = parts[1:]

    if command == "exit":
        return "exit: завершение работы.", True
    elif command == "ls":
        return f"ls: args={args}", False
    elif command == "cd":
        return f"cd: args={args}", False
    else:
        return f"Ошибка: неизвестная команда '{command}'", False


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

        result, should_exit = run_command(line)
        window.print_line(result)

        if should_exit:
            window.root.destroy()
            return

    window.print_line("--- скрипт завершён ---")


class Window:
    """Окно: область вывода + поле ввода."""

    def __init__(self, root, vfs, motd=None, script_path=None):
        self.root = root
        self.vfs = vfs

        root.title(f"Эмулятор - {VFS_NAME}")
        root.geometry("700x450")
        root.minsize(500, 300)

        # Поле ввода — внизу, чтобы всегда было видно
        self.entry = tk.Entry(root, font=("Consolas", 12))
        self.entry.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

        # Область вывода — занимает всё место сверху
        self.output = tk.Text(root, font=("Consolas", 11))
        self.output.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # MOTD — если есть, печатаем до приглашения
        if motd:
            self.print_line(motd)

        self.print_line(f"{VFS_NAME}: введите команду (ls, cd, exit)")

        # Стартовый скрипт — выполняем сразу после старта
        if script_path:
            run_script(self, script_path)

    def print_line(self, text):
        """Добавляет строку в область вывода."""
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def on_enter(self, event):
        """Обработка Enter в поле ввода."""
        text = self.entry.get()
        self.entry.delete(0, tk.END)

        if not text.strip():
            return

        self.print_line(f"{VFS_NAME}$ {text}")

        result, should_exit = run_command(text)
        self.print_line(result)

        if should_exit:
            self.root.destroy()


def main():
    """Точка входа: читает аргументы, грузит VFS, открывает окно."""
    vfs_path, script_path = parse_args(sys.argv[1:])

    print(f"VFS: {vfs_path}")
    print(f"Script: {script_path}")

    # Загружаем VFS — или по умолчанию, если путь не задан
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

    # Ищем motd в корне VFS
    motd = find_motd(vfs)

    root = tk.Tk()
    window = Window(root, vfs, motd=motd, script_path=script_path)

    # Если была ошибка — печатаем её первой строкой после открытия окна
    if vfs_load_error:
        window.output.insert("1.0", vfs_load_error + "\n")

    root.mainloop()


if __name__ == "__main__":
    main()