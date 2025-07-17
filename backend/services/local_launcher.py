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
        # 检测是否在 WSL 中运行
        self.is_wsl = self._detect_wsl()
        
    def create_task_script(self, task_id: str, prompt: str, project_path: str) -> Path:
        """创建任务执行脚本"""
        script_content = self._generate_script_content(task_id, prompt, project_path)
        
        # 根据系统选择脚本扩展名
        if self.is_wsl and self._should_use_windows_terminal():
            ext = '.bat'
        else:
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
        # 如果在 WSL 中运行，但需要启动 Windows 终端
        if self.is_wsl and self._should_use_windows_terminal():
            return self._generate_windows_script(task_id, prompt, project_path)
        elif self.system == 'Windows':
            return self._generate_windows_script(task_id, prompt, project_path)
        else:
            return self._generate_unix_script(task_id, prompt, project_path)
    
    def _generate_windows_script(self, task_id: str, prompt: str, project_path: str) -> str:
        """生成 Windows 批处理脚本"""
        # 转义特殊字符
        prompt_escaped = prompt.replace('"', '""')
        # 转换项目路径为 Windows 格式
        windows_project_path = self._convert_wsl_to_windows_path(project_path)
        
        return f"""@echo off
chcp 65001 > nul
echo ========================================
echo Claude Task Executor
echo Task ID: {task_id}
echo Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
echo ========================================
echo.

cd /d "{windows_project_path}"
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
            # 如果在 WSL 中运行，优先尝试启动 Windows 终端
            if self.is_wsl and self._should_use_windows_terminal():
                return self._launch_windows_terminal(script_path, title)
            elif self.system == "Windows":
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
        # 将 WSL 路径转换为 Windows 路径
        windows_path = self._convert_wsl_to_windows_path(str(script_path))
        
        # 如果在 WSL 中，使用 cmd.exe
        if self.is_wsl:
            try:
                # 在 WSL 中使用 cmd.exe 启动
                subprocess.Popen([
                    'cmd.exe', '/c', 'start',
                    '', f'"{title}"', 'cmd', '/k', windows_path
                ])
                logger.info("从 WSL 使用 cmd.exe 启动 Windows 终端")
                return True
            except Exception as e:
                logger.error(f"WSL 中启动 Windows 终端失败: {e}")
                
        # 尝试使用 Windows Terminal
        try:
            subprocess.Popen([
                'wt', '-w', '0', 'new-tab',
                '--title', title,
                'cmd', '/k', windows_path
            ])
            logger.info("使用 Windows Terminal 启动")
            return True
        except FileNotFoundError:
            pass
        
        # 回退到 CMD
        try:
            if self.is_wsl:
                # WSL 环境不使用 creationflags
                subprocess.Popen([
                    'cmd.exe', '/k',
                    f'title {title} && {windows_path}'
                ])
            else:
                subprocess.Popen([
                    'cmd', '/k',
                    f'title {title} && {windows_path}'
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
    
    def _convert_wsl_to_windows_path(self, wsl_path: str) -> str:
        """将 WSL 路径转换为 Windows 路径"""
        # 检查是否为 WSL 路径格式 /mnt/x/...
        if wsl_path.startswith('/mnt/') and len(wsl_path) > 6:
            drive_letter = wsl_path[5].upper()
            path_part = wsl_path[6:].replace('/', '\\')
            windows_path = f"{drive_letter}:{path_part}"
            logger.info(f"转换路径: {wsl_path} -> {windows_path}")
            return windows_path
        
        # 检查是否为 C:/ 格式（混合格式），转换为 C:\ 格式
        if len(wsl_path) > 2 and wsl_path[1] == ':' and '/' in wsl_path:
            windows_path = wsl_path.replace('/', '\\')
            logger.info(f"转换混合格式路径: {wsl_path} -> {windows_path}")
            return windows_path
        
        # 如果已经是标准 Windows 路径（C:\），直接返回
        if len(wsl_path) > 2 and wsl_path[1] == ':' and '\\' in wsl_path:
            logger.info(f"已是 Windows 路径: {wsl_path}")
            return wsl_path
        
        # 如果是相对路径（如 temp\task_xxx.bat），转换为绝对路径
        if not wsl_path.startswith('/') and not (len(wsl_path) > 1 and wsl_path[1] == ':'):
            # 获取当前工作目录并转换
            try:
                import os
                cwd = os.getcwd()
                full_path = os.path.join(cwd, wsl_path)
                # 递归调用处理完整路径
                return self._convert_wsl_to_windows_path(full_path)
            except:
                pass
            
        # 尝试使用 wslpath 命令转换
        try:
            # 使用 wslpath 命令转换
            result = subprocess.run(['wslpath', '-w', wsl_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                windows_path = result.stdout.strip()
                logger.info(f"使用 wslpath 转换: {wsl_path} -> {windows_path}")
                return windows_path
        except:
            pass
        
        # 默认返回原路径
        logger.warning(f"无法转换路径，使用原路径: {wsl_path}")
        return wsl_path
    
    def _detect_wsl(self) -> bool:
        """检测是否在 WSL 环境中运行"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    def _should_use_windows_terminal(self) -> bool:
        """判断是否应该使用 Windows 终端"""
        # 检查是否有 cmd.exe 可用
        try:
            result = subprocess.run(['which', 'cmd.exe'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
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