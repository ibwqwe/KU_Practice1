@echo off
rem Запуск эмулятора с VFS default.json и стартовым скриптом,
rem который тестирует команды touch и rm.

python src\main.py vfs=vfs\default.json script=scripts\edit_commands.txt
pause