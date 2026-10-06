@echo off
rem Запуск с VFS, у которой более 3 уровней вложенности.

python src\main.py vfs=vfs\nested.json
pause