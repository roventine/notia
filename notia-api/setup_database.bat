@echo off
echo 正在初始化数据库...
cd /d "%~dp0"
python database/init_db.py
echo 数据库初始化完成！
pause