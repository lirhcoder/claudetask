@echo off
:: Claude Code Windows Wrapper
:: 避免 SIGSTOP 信号错误

echo ========================================
echo Claude Code Windows Wrapper
echo ========================================
echo.
echo 提示: 
echo - 使用 Ctrl+C 退出 Claude Code
echo - 不要使用 Ctrl+Z (会导致崩溃)
echo.
echo ----------------------------------------

:: 执行 Claude Code
claude %*

:: 检查退出代码
if %ERRORLEVEL% neq 0 (
    echo.
    echo Claude Code 退出代码: %ERRORLEVEL%
    if %ERRORLEVEL% equ 1 (
        echo 注意: 如果看到 SIGSTOP 错误，请使用 Ctrl+C 代替 Ctrl+Z
    )
)