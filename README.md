# OSEmulator

Эмулятор командной оболочки ОС. Вариант 2, Балкизов И.М. группа ИКБО-20-25.

## О программе

Учебный проект — эмулятор командной строки, похожий на UNIX-подобные оболочки.

Текущий этап — **Этап 3. VFS**.

Что уже умеет:

- окно на Tkinter, в заголовке имя VFS;
- разбор ввода на команду и аргументы;
- команды-заглушки `ls` и `cd`;
- команда `exit`;
- сообщение об ошибке, если команда неизвестна;
- приём аргументов `vfs=` и `script=` при запуске;
- выполнение стартового скрипта с комментариями;
- загрузка VFS из JSON-файла в память;
- вывод `motd` при старте, если файл `motd` лежит в корне VFS;
- VFS по умолчанию, если путь не указан или файл не загрузился.

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

Формат: `имя=значение`. Можно указывать в любом порядке.

- `vfs=<путь>` — путь к JSON-файлу VFS. Если не указан или файл не найден — используется VFS по умолчанию в памяти.
- `script=<путь>` — стартовый скрипт, который эмулятор выполнит при запуске.

Примеры:

```
python src\main.py vfs=vfs\default.json
python src\main.py script=scripts\demo.txt
python src\main.py vfs=vfs\with_motd.json script=scripts\demo.txt
```

## Формат VFS

VFS хранится в JSON-файле. Внутри — дерево папок и файлов.

Каждый узел — либо папка, либо файл:

- папка: `{ "type": "dir", "children": { ... } }`;
- файл: `{ "type": "file", "content": "..." }`;
- двоичные данные кодируются в base64 и помечаются полем `"encoding": "base64"`.

Пример простого файла:

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

## MOTD

Если в корне VFS есть файл `motd`, его содержимое печатается в окне при старте, до приглашения `myVFS$`.

## Готовые файлы VFS

В папке `vfs\` лежат примеры:

- `minimal.json` — только корень, без файлов;
- `default.json` — несколько файлов и папок;
- `nested.json` — минимум 3 уровня вложенности;
- `with_motd.json` — VFS с файлом `motd` в корне.

## Стартовый скрипт

Текстовый файл с командами эмулятора. Что важно:

- строки, начинающиеся с `#`, — комментарии, они пропускаются;
- пустые строки пропускаются;
- если команда неизвестна — выводится ошибка, и работа продолжается;
- в окне видно и ввод, и вывод — как будто пользователь вводит команды руками.

## Скрипты для запуска

В папке `scripts\os_scripts\` лежат `.bat`-файлы для разных сценариев:

Без VFS:

- `run_default.bat` — без аргументов;
- `run_with_vfs.bat` — только `vfs=C:\data` (несуществующий путь, проверка VFS по умолчанию);
- `run_with_script.bat` — только `script=scripts\demo.txt`;
- `run_all.bat` — оба аргумента;
- `run_errors.bat` — проверка обработки ошибок.

С VFS:

- `run_vfs_minimal.bat` — с `vfs\minimal.json`;
- `run_vfs_default.bat` — с `vfs\default.json`;
- `run_vfs_nested.bat` — с `vfs\nested.json`;
- `run_vfs_motd.bat` — с `vfs\with_motd.json`;
- `run_vfs_broken.bat` — с несуществующим файлом (проверка ошибки).

## Файлы проекта

```
PythonProject\
├── README.md
├── .gitignore
├── run.bat
├── src\
│   └── main.py
├── tests\
├── scripts\
│   ├── demo.txt
│   ├── errors.txt
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
│       └── run_vfs_broken.bat
└── vfs\
    ├── minimal.json
    ├── default.json
    ├── nested.json
    └── with_motd.json
```

## Функции в src\main.py

- `parse_args(argv)` — разбирает `vfs=` и `script=`.
- `make_default_vfs()` — VFS по умолчанию, если путь не указан.
- `load_vfs(path)` — читает JSON-файл VFS, возвращает `(vfs, ошибка)`.
- `find_motd(vfs)` — ищет файл `motd` в корне VFS.
- `run_command(text)` — выполняет одну команду, возвращает ответ и флаг выхода.
- `run_script(window, path)` — открывает файл скрипта и выполняет его построчно.
- `Window` — класс окна: область вывода, поле ввода, приветствие.
- `main()` — точка входа.

Настройка в коде: `VFS_NAME = "myVFS"` — имя VFS в заголовке окна и приглашении.

## Пример работы

Запуск с VFS, содержащей motd:

```
python src\main.py vfs=vfs\with_motd.json
```

Окно:

```
Добро пожаловать в myVFS!
Сегодня хороший день для тестирования.
myVFS: введите команду (ls, cd, exit)
myVFS$ _
```

Запуск с несуществующим VFS:

```
python src\main.py vfs=vfs\fake.json
```

Окно:

```
Ошибка загрузки VFS: файл не найден: vfs\fake.json
myVFS: введите команду (ls, cd, exit)
myVFS$ _
```

Программа не падает — используется VFS по умолчанию.

## Требования

- Python 3.10+
- Tkinter (входит в Python)