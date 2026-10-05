import tkinter as tk

VFS_NAME = "VFS"  # имя виртуальной файловой системы


def run_command(text):
    """Разбирает строку на команду и аргументы и выполняет её."""
    parts = text.split()          # делим по пробелам
    command = parts[0]            # первое слово — команда
    args = parts[1:]              # остальное — аргументы

    if command == "exit":
        return "exit: завершение работы.", True
    elif command == "ls":
        return f"ls: args={args}", False
    elif command == "cd":
        return f"cd: args={args}", False
    else:
        return f"Ошибка: неизвестная команда '{command}'", False


def on_enter(event):
    """Обработчик нажатия Enter в поле ввода."""
    text = entry.get()            # читаем ввод
    entry.delete(0, tk.END)       # очищаем поле

    if not text.strip():
        return

    # Показываем ввод пользователя
    output.insert(tk.END, f"{VFS_NAME}$ {text}\n")

    # Выполняем команду и показываем результат
    result, should_exit = run_command(text)
    output.insert(tk.END, result + "\n")
    output.see(tk.END)

    if should_exit:
        root.destroy()


# --- Создаём окно ---
root = tk.Tk()
root.title(f"Эмулятор - {VFS_NAME}")   # заголовок с именем VFS
root.geometry("700x400")

# Область вывода
output = tk.Text(root, font=("Consolas", 11))
output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Поле ввода
entry = tk.Entry(root, font=("Consolas", 12))
entry.pack(fill=tk.X, padx=5, pady=(0, 5))
entry.bind("<Return>", on_enter)
entry.focus_set()

# Приветствие
output.insert(tk.END, f"{VFS_NAME}: введите команду (ls, cd, exit)\n")

root.mainloop()
