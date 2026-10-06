@echo off
rem Запуск с несуществующим файлом VFS — проверка обработки ошибки.

python src\main.py vfs=vfs\does_not_exist.json
pause