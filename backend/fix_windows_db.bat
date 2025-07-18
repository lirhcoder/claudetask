@echo off
echo === 修复 Windows 数据库兼容性问题 ===
echo.

cd /d "%~dp0"

if exist "tasks.db" (
    echo 找到数据库文件: tasks.db
    python fix_windows_db.py tasks.db
) else (
    echo 错误: 未找到 tasks.db
    echo 请在后端目录中运行此脚本
)

echo.
echo 完成后请重新启动 Flask 应用:
echo   python run.py
echo.
pause