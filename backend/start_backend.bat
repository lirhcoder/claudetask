@echo off
REM Windows 启动脚本

echo === ClaudeTask 后端启动脚本 ===

cd /d "%~dp0"

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 找到虚拟环境
    
    REM 激活虚拟环境
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
    
    REM 检查 Flask
    python -c "import flask" 2>nul
    if errorlevel 1 (
        echo Flask 未安装，正在安装依赖...
        pip install -r requirements.txt
    ) else (
        echo Flask 已安装
    )
) else (
    echo 未找到虚拟环境
    echo 请先创建虚拟环境：
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM 检查数据库
if exist "tasks.db" (
    echo 数据库文件存在
) else (
    echo 数据库文件不存在，创建管理员账号...
    python create_admin.py
)

echo.
echo 可用的登录账号：
echo   管理员: admin@claudetask.local / admin123
echo   或运行: python create_admin.py 创建 admin@sparticle.com
echo.

REM 启动 Flask
echo 启动 Flask 应用...
echo   访问地址: http://localhost:5000
echo   按 Ctrl+C 停止服务
echo.

python run.py
pause