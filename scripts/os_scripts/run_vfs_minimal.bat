@echo off
rem Запуск с минимальной VFS (только корень, без файлов).

python src\main.py vfs=vfs\minimal.json
pause