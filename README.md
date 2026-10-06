# OSEmulator

Эмулятор командной оболочки ОС. Вариант 2, Балкизов И.М. группа ИКБО-20-25.

## О программе

Учебный проект — эмулятор командной строки, похожий на UNIX-подобные оболочки.

Текущий этап — **Этап 4. Основные команды**.

Что уже умеет:

- окно на Tkinter, в заголовке имя VFS;
- разбор ввода на команду и аргументы;
- рабочие команды `ls`, `cd`, `cat`, `tac`;
- команда `exit`;
- обработка ошибок;
- приём аргументов `vfs=` и `script=` при запуске;
- выполнение стартового скрипта с комментариями;
- загрузка VFS из JSON-файла в память;
- вывод `motd` при старте, если файл `motd` лежит в корне VFS;
- VFS по умолчанию, если путь не указан или файл не загрузился;
- навигация по VFS: текущая директория, переходы `..` и `/`.

## Запуск

Запускать нужно из корня проекта.

Обычный запуск:

```
run.bat
```

Или напрямую:

```
python src\main.py
```

## Аргументы командной строки

Формат: `имя=значение`.

- `vfs=<путь>` — путь к JSON-файлу VFS. Если не указан или файл не найден — используется VFS по умолчанию.
- `script=<путь>` — стартовый скрипт, который эмулятор выполнит при запуске.

Примеры:

```
python src\main.py vfs=vfs\default.json
python src\main.py script=scripts\demo.txt
python src\main.py vfs=vfs\default.json script=scripts\vfs_commands.txt
```

## Поддерживаемые команды

### ls

Показывает содержимое папки или имя файла. Без аргументов — текущая директория.

```
myVFS$ ls
etc
home
notes.md
readme.txt

myVFS$ ls home
user

myVFS$ ls readme.txt
readme.txt
```

### cd

Меняет текущую директорию. Без аргументов — переход в корень.

```
myVFS$ cd home
myVFS$ cd user
myVFS$ cd ..
myVFS$ cd /
```

При успехе `cd` ничего не печатает.

### cat

Выводит содержимое файла.

```
myVFS$ cat readme.txt
Это стандартная VFS для тестирования.

myVFS$ cat home/user/config.ini
[settings]
theme=dark
```

### tac

Как `cat`, но строки в обратном порядке.

```
myVFS$ tac home/user/config.ini
theme=dark
[settings]
```

### exit

Завершает работу приложения.

## Обработка ошибок

Неизвестная команда:

```
myVFS$ abc
Ошибка: неизвестная команда 'abc'
```

Несуществующий путь:

```
myVFS$ cd missing
cd: путь не найден: /missing
```

`cat` / `tac` на папку:

```
myVFS$ cat home
cat: это папка: home
```

`cd` на файл:

```
myVFS$ cd readme.txt
cd: не папка: readme.txt
```

## Формат VFS

VFS хранится в JSON-файле. Внутри — дерево папок и файлов.

Каждый узел — либо папка, либо файл:

- папка: `{ "type": "dir", "children": { ... } }`;
- файл: `{ "type": "file", "content": "..." }`;
- двоичные данные кодируются в base64 и помечаются полем `"encoding": "base64"`.

Пример:

```json
{
  "name": "default",
  "root": {
    "type": "dir",
    "children": {
      "readme.txt": {
        "type": "file",
        "content": "Пример."
      },
      "docs": {
        "type": "dir",
        "children": {}
      }
    }
  }
}
```

Все операции с VFS выполняются в памяти. JSON-файл только читается — не изменяется.

## Готовые файлы VFS

В папке `vfs\`:

- `minimal.json` — только корень, без файлов;
- `default.json` — несколько файлов и папок;
- `nested.json` — минимум 3 уровня вложенности;
- `with_motd.json` — VFS с файлом `motd` в корне.

## MOTD

Если в корне VFS есть файл `motd`, его содержимое печатается при старте, до приглашения `myVFS$`.

## Стартовые скрипты

Текстовые файлы с командами эмулятора. Что важно:

- строки, начинающиеся с `#`, — комментарии, они пропускаются;
- пустые строки пропускаются;
- если команда неизвестна — выводится ошибка, и работа продолжается;
- в окне видно и ввод, и вывод.

В папке `scripts\`:

- `demo.txt` — демонстрация работы `ls` и `cd`;
- `errors.txt` — проверка обработки ошибок;
- `vfs_commands.txt` — полное тестирование всех команд этапа 4.

## Скрипты для запуска

В папке `scripts\os_scripts\`:

- `run_default.bat` — без аргументов;
- `run_with_vfs.bat` — только `vfs=C:\data`;
- `run_with_script.bat` — только `script=scripts\demo.txt`;
- `run_all.bat` — оба аргумента;
- `run_errors.bat` — скрипт с ошибками;
- `run_vfs_minimal.bat` — с `vfs\minimal.json`;
- `run_vfs_default.bat` — с `vfs\default.json`;
- `run_vfs_nested.bat` — с `vfs\nested.json`;
- `run_vfs_motd.bat` — с `vfs\with_motd.json`;
- `run_vfs_broken.bat` — с несуществующим файлом;
- `run_vfs_commands.bat` — тестирование команд `ls`, `cd`, `cat`, `tac`.

## Файлы проекта

```
PythonProject\
├── README.md
├── .gitignore
├── run.bat
├── src\
│   └── main.py
├── tests\
│   └── (тесты или .gitkeep)
├── scripts\
│   ├── demo.txt
│   ├── errors.txt
│   ├── vfs_commands.txt
│   └── os_scripts\
│       ├── run_default.bat
│       ├── run_with_vfs.bat
│       ├── run_with_script.bat
│       ├── run_all.bat
│       ├── run_errors.bat
│       ├── run_vfs_minimal.bat
│       ├── run_vfs_default.bat
│       ├── run_vfs_nested.bat
│       ├── run_vfs_motd.bat
│       ├── run_vfs_broken.bat
│       └── run_vfs_commands.bat
└── vfs\
    ├── minimal.json
    ├── default.json
    ├── nested.json
    └── with_motd.json
```

## Функции в src\main.py

- `parse_args(argv)` — разбирает `vfs=` и `script=`.
- `make_default_vfs()` — VFS по умолчанию.
- `load_vfs(path)` — читает JSON-файл VFS.
- `find_motd(vfs)` — ищет `motd` в корне VFS.
- `split_path(path)` — разбивает путь на части.
- `get_node(vfs, cwd, path)` — находит узел по пути.
- `cmd_ls`, `cmd_cd`, `cmd_cat`, `cmd_tac` — команды.
- `run_script(window, path)` — выполняет стартовый скрипт.
- `Window` — окно: область вывода, поле ввода, обработка команд.
- `main()` — точка входа.

Настройка: `VFS_NAME = "myVFS"` — имя VFS в заголовке окна и приглашении.

## Пример работы

```
myVFS: введите команду (ls, cd, cat, tac, exit)
myVFS$ ls
etc
home
notes.md
readme.txt
myVFS$ cd home
myVFS$ ls
user
myVFS$ cd user
myVFS$ ls
config.ini
myVFS$ cat config.ini
[settings]
theme=dark
myVFS$ tac config.ini
theme=dark
[settings]
myVFS$ cd /
myVFS$ cat home/user/config.ini
[settings]
theme=dark
myVFS$ cd missing
cd: путь не найден: /missing
myVFS$ cat home
cat: это папка: home
myVFS$ exit
exit: завершение работы.
```

## Требования

- Python 3.10+
- Tkinter (входит в Python)