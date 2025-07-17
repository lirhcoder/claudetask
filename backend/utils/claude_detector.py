import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional

def detect_claude_path() -> Optional[str]:
    """
    自动检测 Claude CLI 的路径
    
    Returns:
        Claude 可执行文件的路径，如果找不到返回 None
    """
    system = platform.system()
    
    # 1. 先检查环境变量是否已设置
    env_path = os.environ.get('CLAUDE_CODE_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    
    # 2. 使用 shutil.which 查找系统 PATH 中的 claude
    claude_in_path = shutil.which('claude')
    if claude_in_path:
        return claude_in_path
    
    # 3. 根据不同系统检查常见安装位置
    common_paths = []
    
    if system == 'Windows':
        # Windows 常见安装路径
        user_home = Path.home()
        common_paths.extend([
            # 用户 AppData
            user_home / 'AppData' / 'Local' / 'Programs' / 'claude' / 'claude.exe',
            user_home / 'AppData' / 'Local' / 'claude' / 'claude.exe',
            # Program Files
            Path('C:/Program Files/claude/claude.exe'),
            Path('C:/Program Files (x86)/claude/claude.exe'),
            # 用户目录
            user_home / '.claude' / 'bin' / 'claude.exe',
            user_home / 'claude' / 'claude.exe',
        ])
        
        # Windows 特殊：检查带不同扩展名的版本
        for ext in ['.exe', '.cmd', '.bat']:
            ext_path = shutil.which(f'claude{ext}')
            if ext_path:
                return ext_path
                
    elif system == 'Linux':
        # Linux/WSL 常见安装路径
        user_home = Path.home()
        common_paths.extend([
            # 系统级安装
            Path('/usr/local/bin/claude'),
            Path('/usr/bin/claude'),
            Path('/opt/claude/claude'),
            # 用户级安装
            user_home / '.local' / 'bin' / 'claude',
            user_home / '.claude' / 'bin' / 'claude',
            user_home / 'bin' / 'claude',
            # Snap
            Path('/snap/bin/claude'),
        ])
        
    elif system == 'Darwin':  # macOS
        # macOS 常见安装路径
        user_home = Path.home()
        common_paths.extend([
            # Homebrew
            Path('/usr/local/bin/claude'),
            Path('/opt/homebrew/bin/claude'),
            # 用户级安装
            user_home / '.local' / 'bin' / 'claude',
            user_home / '.claude' / 'bin' / 'claude',
            user_home / 'bin' / 'claude',
            # Applications
            Path('/Applications/Claude.app/Contents/MacOS/claude'),
        ])
    
    # 检查常见路径
    for path in common_paths:
        if path.exists():
            return str(path)
    
    # 4. 尝试使用系统命令查找 (仅限 Unix-like 系统)
    if system in ['Linux', 'Darwin']:
        try:
            result = subprocess.run(['which', 'claude'], 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
    
    # 5. Windows 特殊：使用 where 命令
    if system == 'Windows':
        try:
            result = subprocess.run(['where', 'claude'], 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                # where 可能返回多行，取第一行
                return result.stdout.strip().split('\n')[0]
        except:
            pass
    
    return None


def get_environment_info():
    """获取当前环境信息"""
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'is_wsl': False,
        'is_docker': False,
    }
    
    # 检测 WSL
    if info['system'] == 'Linux':
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    info['is_wsl'] = True
        except:
            pass
    
    # 检测 Docker
    if os.path.exists('/.dockerenv'):
        info['is_docker'] = True
    
    return info


def create_environment_config():
    """根据环境创建配置文件"""
    env_info = get_environment_info()
    claude_path = detect_claude_path()
    
    config = {
        'environment': env_info,
        'claude_path': claude_path,
        'recommendations': []
    }
    
    if not claude_path:
        config['recommendations'].append(
            "Claude CLI not found. Please install Claude Code from: "
            "https://github.com/anthropics/claude-code"
        )
        
        if env_info['system'] == 'Windows':
            config['recommendations'].append(
                "For Windows, add Claude to your PATH or set CLAUDE_CODE_PATH "
                "environment variable to the full path of claude.exe"
            )
        elif env_info['is_wsl']:
            config['recommendations'].append(
                "For WSL, you can install Claude using: "
                "curl -fsSL https://claude.ai/install.sh | sh"
            )
    
    return config


if __name__ == '__main__':
    # 测试自动检测
    import json
    
    print("Detecting Claude CLI...")
    config = create_environment_config()
    
    print("\nEnvironment Info:")
    print(json.dumps(config['environment'], indent=2))
    
    print("\nClaude Path:", config['claude_path'] or "Not found")
    
    if config['recommendations']:
        print("\nRecommendations:")
        for rec in config['recommendations']:
            print(f"- {rec}")