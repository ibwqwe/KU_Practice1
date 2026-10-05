"""
Эмулятор оболочки. Этап 2: конфигурация через аргументы командной строки.
"""

import sys
import tkinter as tk

VFS_NAME = "myVFS"


def parse_args(argv):
    """Разбирает аргументы вида vfs=... и script=... ."""
    vfs_path = None
    script_path = None

    for arg in argv:
        if arg.startswith("vfs="):
            vfs_path = arg[4:]      # отрезаем "vfs="
        elif arg.startswith("script="):
            script_path = arg[7:]   # отрезаем "script="
        else:
            print(f"Неизвестный аргумент: {arg}")

    return vfs_path, script_path


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

        # Пустые строки и комментарии пропускаем
        if not line or line.startswith("#"):
            continue

        # Эхо ввода — как будто пользователь ввёл
        window.print_line(f"{VFS_NAME}$ {line}")

        # Выполняем и печатаем результат
        result, should_exit = run_command(line)
        window.print_line(result)

        if should_exit:
            window.root.destroy()
            return

    window.print_line("--- скрипт завершён ---")


class Window:
    """Простое окно: область вывода + поле ввода."""

    def __init__(self, root, script_path=None):
        self.root = root
        root.title(f"Эмулятор - {VFS_NAME}")
        root.geometry("700x450")

        self.entry = tk.Entry(root, font=("Consolas", 12))
        self.entry.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

        self.output = tk.Text(root, font=("Consolas", 11))
        self.output.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.print_line(f"{VFS_NAME}: введите команду (ls, cd, exit)")

        # Если передан скрипт — выполняем его сразу после старта
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
    """Точка входа: читает аргументы, открывает окно."""
    vfs_path, script_path = parse_args(sys.argv[1:])

    # Отладочная печать — видно, что передали
    print(f"VFS: {vfs_path}")
    print(f"Script: {script_path}")

    root = tk.Tk()
    Window(root, script_path)
    root.mainloop()


if __name__ == "__main__":
    main()