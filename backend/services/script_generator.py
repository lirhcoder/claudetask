"""
任务脚本生成器 - 生成可在本地执行的 Claude 脚本
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class TaskScriptGenerator:
    """生成不同平台的任务执行脚本"""
    
    def __init__(self, claude_path: Optional[str] = None):
        self.claude_path = claude_path or os.environ.get('CLAUDE_CODE_PATH', 'claude')
        
    def generate_interactive_script(self, task_id: str, prompt: str, project_path: str) -> Dict[str, str]:
        """生成支持交互的脚本"""
        return {
            'windows': self._generate_windows_interactive(task_id, prompt, project_path),
            'unix': self._generate_unix_interactive(task_id, prompt, project_path)
        }
    
    def _generate_windows_interactive(self, task_id: str, prompt: str, project_path: str) -> str:
        """生成支持交互的 Windows 脚本"""
        prompt_escaped = prompt.replace('"', '""')
        
        return f"""@echo off
chcp 65001 > nul
title Claude Interactive Task - {task_id[:8]}
color 0A

echo ╔════════════════════════════════════════════════════════════╗
echo ║              Claude Code Interactive Executor              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📋 Task ID: {task_id}
echo 📅 Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
echo 📁 Project: {project_path}
echo.
echo ════════════════════════════════════════════════════════════
echo.

:: 切换到项目目录
cd /d "{project_path}"
if errorlevel 1 (
    echo ❌ Error: Cannot access project directory
    pause
    exit /b 1
)

echo 📂 Working Directory: %CD%
echo.
echo 💬 Prompt:
echo {prompt}
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo ▶️  Starting Claude Code in interactive mode...
echo     You can interact with Claude during execution.
echo.

:: 执行 Claude 命令
{self.claude_path} "{prompt_escaped}"

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ Task completed!
echo.
echo Press any key to close this window...
pause > nul
"""
    
    def _generate_unix_interactive(self, task_id: str, prompt: str, project_path: str) -> str:
        """生成支持交互的 Unix 脚本"""
        prompt_escaped = prompt.replace('"', '\\"').replace('$', '\\$')
        
        return f"""#!/bin/bash

# 设置颜色
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m' # No Color

clear

echo -e "${{GREEN}}╔════════════════════════════════════════════════════════════╗${{NC}}"
echo -e "${{GREEN}}║              Claude Code Interactive Executor              ║${{NC}}"
echo -e "${{GREEN}}╚════════════════════════════════════════════════════════════╝${{NC}}"
echo
echo -e "${{BLUE}}📋 Task ID:${{NC}} {task_id}"
echo -e "${{BLUE}}📅 Created:${{NC}} $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${{BLUE}}📁 Project:${{NC}} {project_path}"
echo
echo "════════════════════════════════════════════════════════════"
echo

# 切换到项目目录
cd "{project_path}" || {{
    echo -e "${{RED}}❌ Error: Cannot access project directory${{NC}}"
    read -p "Press Enter to exit..."
    exit 1
}}

echo -e "${{BLUE}}📂 Working Directory:${{NC}} $(pwd)"
echo
echo -e "${{BLUE}}💬 Prompt:${{NC}}"
echo "{prompt}"
echo
echo "════════════════════════════════════════════════════════════"
echo
echo -e "${{YELLOW}}▶️  Starting Claude Code in interactive mode...${{NC}}"
echo "    You can interact with Claude during execution."
echo

# 执行 Claude 命令
{self.claude_path} "{prompt_escaped}"

echo
echo "════════════════════════════════════════════════════════════"
echo -e "${{GREEN}}✅ Task completed!${{NC}}"
echo
read -p "Press Enter to close this window..."
"""
    
    def generate_context_script(self, task_id: str, prompt: str, project_path: str, 
                              context: Optional[str] = None) -> Dict[str, str]:
        """生成包含上下文的脚本"""
        # 如果有上下文，将其添加到提示中
        if context:
            full_prompt = f"{context}\n\n当前任务：\n{prompt}"
        else:
            full_prompt = prompt
            
        return self.generate_interactive_script(task_id, full_prompt, project_path)
    
    def generate_chain_script(self, parent_task_id: str, tasks: list, project_path: str) -> Dict[str, str]:
        """生成任务链脚本"""
        return {
            'windows': self._generate_windows_chain(parent_task_id, tasks, project_path),
            'unix': self._generate_unix_chain(parent_task_id, tasks, project_path)
        }
    
    def _generate_windows_chain(self, parent_task_id: str, tasks: list, project_path: str) -> str:
        """生成 Windows 任务链脚本"""
        script = f"""@echo off
chcp 65001 > nul
title Claude Task Chain - {parent_task_id[:8]}

echo ╔════════════════════════════════════════════════════════════╗
echo ║              Claude Code Task Chain Executor               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📋 Chain ID: {parent_task_id}
echo 📅 Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
echo 🔗 Total Tasks: {len(tasks)}
echo.

cd /d "{project_path}"

"""
        for i, task in enumerate(tasks):
            prompt_escaped = task['prompt'].replace('"', '""')
            script += f"""
echo ════════════════════════════════════════════════════════════
echo 📌 Task {i+1}/{len(tasks)}: {task.get('description', 'Task ' + str(i+1))}
echo ════════════════════════════════════════════════════════════
echo.

{self.claude_path} "{prompt_escaped}"

if errorlevel 1 (
    echo ❌ Task {i+1} failed!
    pause
    exit /b 1
)

echo ✅ Task {i+1} completed!
echo.
"""
        
        script += """
echo ════════════════════════════════════════════════════════════
echo 🎉 All tasks completed successfully!
pause
"""
        return script
    
    def _generate_unix_chain(self, parent_task_id: str, tasks: list, project_path: str) -> str:
        """生成 Unix 任务链脚本"""
        script = f"""#!/bin/bash

GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
RED='\\033[0;31m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

clear

echo -e "${{GREEN}}╔════════════════════════════════════════════════════════════╗${{NC}}"
echo -e "${{GREEN}}║              Claude Code Task Chain Executor               ║${{NC}}"
echo -e "${{GREEN}}╚════════════════════════════════════════════════════════════╝${{NC}}"
echo
echo -e "${{BLUE}}📋 Chain ID:${{NC}} {parent_task_id}"
echo -e "${{BLUE}}📅 Created:${{NC}} $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${{BLUE}}🔗 Total Tasks:${{NC}} {len(tasks)}"
echo

cd "{project_path}" || exit 1

"""
        for i, task in enumerate(tasks):
            prompt_escaped = task['prompt'].replace('"', '\\"').replace('$', '\\$')
            script += f"""
echo "════════════════════════════════════════════════════════════"
echo -e "${{YELLOW}}📌 Task {i+1}/{len(tasks)}: {task.get('description', 'Task ' + str(i+1))}${{NC}}"
echo "════════════════════════════════════════════════════════════"
echo

{self.claude_path} "{prompt_escaped}"

if [ $? -ne 0 ]; then
    echo -e "${{RED}}❌ Task {i+1} failed!${{NC}}"
    read -p "Press Enter to exit..."
    exit 1
fi

echo -e "${{GREEN}}✅ Task {i+1} completed!${{NC}}"
echo
"""
        
        script += """
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}🎉 All tasks completed successfully!${NC}"
read -p "Press Enter to close..."
"""
        return script