@echo off
echo ============================================
echo     ClaudeTask GitHub 风格迁移工具
echo ============================================
echo.
echo 此脚本将帮助您将系统迁移到 GitHub 风格的架构
echo.
echo 迁移内容：
echo   - 项目 → 仓库
echo   - 任务 → 分支
echo   - 旧 API → 新 API（保持兼容）
echo.
echo 按任意键开始迁移，或按 Ctrl+C 取消...
pause > nul

python migrate_to_github.py

echo.
echo 迁移完成！请重启后端服务。
pause