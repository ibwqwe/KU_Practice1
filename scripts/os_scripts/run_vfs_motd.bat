@echo off
rem Запуск с VFS, содержащей motd в корне.
rem В окне должно появиться приветствие.

python src\main.py vfs=vfs\with_motd.json
pause