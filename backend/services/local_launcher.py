"""
本地工具启动器 - 在本地终端中启动 Claude CLI
"""
import os
import sys
import platform
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class LocalLauncher:
    """启动本地终端执行 Claude 任务"""
    
    def __init__(self, temp_dir: str = "temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.system = platform.system()
        
    def create_task_script(self, task_id: str, prompt: str, project_path: str) -> Path:
        """创建任务执行脚本"""
        script_content = self._generate_script_content(task_id, prompt, project_path)
        
        # 根据系统选择脚本扩展名
        ext = '.bat' if self.system == 'Windows' else '.sh'
        script_path = self.temp_dir / f'task_{task_id}{ext}'
        
        # 写入脚本内容
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Unix 系统设置执行权限
        if self.system != 'Windows':
            os.chmod(script_path, 0o755)
        
        logger.info(f"创建任务脚本: {script_path}")
        return script_path
    
    def _generate_script_content(self, task_id: str, prompt: str, project_path: str) -> str:
        """生成脚本内容"""
        if self.system == 'Windows':
            return self._generate_windows_script(task_id, prompt, project_path)
        else:
            return self._generate_unix_script(task_id, prompt, project_path)
    
    def _generate_windows_script(self, task_id: str, prompt: str, project_path: str) -> str:
        """生成 Windows 批处理脚本"""
        # 转义特殊字符
        prompt_escaped = prompt.replace('"', '""')
        
        return f"""@echo off
chcp 65001 > nul
echo ========================================
echo Claude Task Executor
echo Task ID: {task_id}
echo Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
echo ========================================
echo.

cd /d "{project_path}"
echo Working Directory: %CD%
echo.

echo Executing Claude Code...
echo ----------------------------------------
claude "{prompt_escaped}"

echo.
echo ----------------------------------------
echo Task completed. Press any key to close...
pause > nul
"""
    
    def _generate_unix_script(self, task_id: str, prompt: str, project_path: str) -> str:
        """生成 Unix Shell 脚本"""
        # 转义特殊字符
        prompt_escaped = prompt.replace('"', '\\"').replace('$', '\\$')
        
        return f"""#!/bin/bash
echo "========================================"
echo "Claude Task Executor"
echo "Task ID: {task_id}"
echo "Created: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo

cd "{project_path}"
echo "Working Directory: $(pwd)"
echo

echo "Executing Claude Code..."
echo "----------------------------------------"
claude "{prompt_escaped}"

echo
echo "----------------------------------------"
echo "Task completed. Press Enter to close..."
read
"""
    
    def launch_terminal(self, script_path: Path, title: str = "Claude Task") -> bool:
        """启动终端执行脚本"""
        try:
            if self.system == "Windows":
                return self._launch_windows_terminal(script_path, title)
            elif self.system == "Darwin":  # macOS
                return self._launch_macos_terminal(script_path, title)
            else:  # Linux
                return self._launch_linux_terminal(script_path, title)
        except Exception as e:
            logger.error(f"启动终端失败: {str(e)}")
            return False
    
    def _launch_windows_terminal(self, script_path: Path, title: str) -> bool:
        """启动 Windows 终端"""
        # 尝试使用 Windows Terminal
        try:
            subprocess.Popen([
                'wt', '-w', '0', 'new-tab',
                '--title', title,
                'cmd', '/k', str(script_path)
            ])
            logger.info("使用 Windows Terminal 启动")
            return True
        except FileNotFoundError:
            pass
        
        # 回退到 CMD
        try:
            subprocess.Popen([
                'cmd', '/k',
                f'title {title} && {script_path}'
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            logger.info("使用 CMD 启动")
            return True
        except Exception as e:
            logger.error(f"Windows 终端启动失败: {e}")
            return False
    
    def _launch_macos_terminal(self, script_path: Path, title: str) -> bool:
        """启动 macOS 终端"""
        try:
            # 使用 AppleScript 启动 Terminal.app
            applescript = f'''
            tell application "Terminal"
                activate
                do script "{script_path}"
                set custom title of front window to "{title}"
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript], check=True)
            logger.info("使用 Terminal.app 启动")
            return True
        except Exception as e:
            logger.error(f"macOS 终端启动失败: {e}")
            return False
    
    def _launch_linux_terminal(self, script_path: Path, title: str) -> bool:
        """启动 Linux 终端"""
        # 尝试不同的终端模拟器
        terminals = [
            ['gnome-terminal', '--', 'bash', str(script_path)],
            ['konsole', '-e', 'bash', str(script_path)],
            ['xfce4-terminal', '-e', f'bash {script_path}'],
            ['xterm', '-T', title, '-e', 'bash', str(script_path)],
            ['x-terminal-emulator', '-e', f'bash {script_path}']
        ]
        
        for terminal_cmd in terminals:
            try:
                subprocess.Popen(terminal_cmd)
                logger.info(f"使用 {terminal_cmd[0]} 启动")
                return True
            except FileNotFoundError:
                continue
        
        logger.error("未找到可用的 Linux 终端")
        return False
    
    def create_task_info(self, task_id: str, prompt: str, project_path: str) -> Path:
        """创建任务信息文件"""
        info = {
            'task_id': task_id,
            'prompt': prompt,
            'project_path': project_path,
            'created_at': datetime.now().isoformat(),
            'system': self.system
        }
        
        info_path = self.temp_dir / f'task_{task_id}_info.json'
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        return info_path
    
    def cleanup_old_scripts(self, days: int = 7):
        """清理旧的脚本文件"""
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for file in self.temp_dir.glob('task_*'):
            if file.stat().st_mtime < cutoff_time:
                try:
                    file.unlink()
                    logger.info(f"删除旧脚本: {file}")
                except Exception as e:
                    logger.error(f"删除失败: {file}, {e}")