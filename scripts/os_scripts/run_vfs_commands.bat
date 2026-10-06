@echo off
rem Запуск эмулятора с VFS default.json и стартовым скриптом,
rem который тестирует команды ls, cd, cat, tac.

python src\main.py vfs=vfs\default.json script=scripts\vfs_commands.txt
pause