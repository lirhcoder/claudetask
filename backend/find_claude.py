#!/usr/bin/env python3
"""
查找 Claude CLI 的辅助脚本
支持 Windows 和 WSL 环境
"""
import os
import subprocess
import platform

def find_claude_windows():
    """在 Windows 中查找 Claude"""
    print("在 Windows 中搜索 Claude...")
    
    # 1. 检查 PATH 环境变量
    print("\n1. 检查 PATH 环境变量:")
    path_dirs = os.environ.get('PATH', '').split(';')
    for dir in path_dirs:
        if dir and os.path.exists(dir):
            # 检查各种可能的文件名
            for name in ['claude.exe', 'claude.cmd', 'claude.bat', 'claude']:
                full_path = os.path.join(dir, name)
                if os.path.exists(full_path):
                    print(f"  ✓ 找到: {full_path}")
                    return full_path
    print("  ✗ PATH 中未找到 Claude")
    
    # 2. 使用 where 命令
    print("\n2. 使用 where 命令搜索:")
    try:
        for cmd in ['claude', 'claude.exe', 'claude.cmd']:
            result = subprocess.run(['where', cmd], 
                                  capture_output=True, 
                                  text=True, 
                                  shell=True)
            if result.returncode == 0:
                paths = result.stdout.strip().split('\n')
                for path in paths:
                    if path:
                        print(f"  ✓ 找到: {path}")
                        return path
    except Exception as e:
        print(f"  ✗ where 命令失败: {e}")
    
    # 3. 检查常见安装位置
    print("\n3. 检查常见安装位置:")
    user_home = os.path.expanduser("~")
    common_locations = [
        # npm/yarn 全局安装
        os.path.join(user_home, "AppData", "Roaming", "npm", "claude.cmd"),
        os.path.join(user_home, "AppData", "Roaming", "npm", "claude.exe"),
        os.path.join(user_home, "AppData", "Roaming", "npm", "claude"),
        # Yarn 全局
        os.path.join(user_home, "AppData", "Local", "Yarn", "bin", "claude.cmd"),
        # scoop
        os.path.join(user_home, "scoop", "shims", "claude.cmd"),
        # chocolatey
        "C:\\ProgramData\\chocolatey\\bin\\claude.exe",
        # 直接安装
        os.path.join(user_home, "AppData", "Local", "Programs", "claude", "claude.exe"),
        "C:\\Program Files\\claude\\claude.exe",
        "C:\\Program Files (x86)\\claude\\claude.exe",
        # WSL 路径（如果从 Windows 访问）
        "C:\\Windows\\System32\\wsl.exe",
    ]
    
    for location in common_locations:
        if os.path.exists(location):
            print(f"  ✓ 找到: {location}")
            
            # 如果是 npm/yarn 安装的 .cmd 文件，尝试找到实际的可执行文件
            if location.endswith('.cmd'):
                print(f"    (这是一个批处理文件，Claude 实际可能通过 Node.js 运行)")
            
            return location
    
    print("  ✗ 常见位置未找到 Claude")
    
    # 4. 检查 Node.js 全局包
    print("\n4. 检查 Node.js 全局包:")
    try:
        # 检查 npm
        result = subprocess.run(['npm', 'list', '-g', 'claude'], 
                              capture_output=True, 
                              text=True, 
                              shell=True)
        if 'claude@' in result.stdout:
            print("  ✓ Claude 已通过 npm 全局安装")
            # 获取 npm 全局目录
            npm_result = subprocess.run(['npm', 'config', 'get', 'prefix'], 
                                      capture_output=True, 
                                      text=True, 
                                      shell=True)
            if npm_result.returncode == 0:
                npm_prefix = npm_result.stdout.strip()
                claude_cmd = os.path.join(npm_prefix, 'claude.cmd')
                if os.path.exists(claude_cmd):
                    print(f"  ✓ 找到: {claude_cmd}")
                    return claude_cmd
    except:
        pass
    
    return None


def check_wsl_claude():
    """检查是否可以通过 WSL 访问 Claude"""
    print("\n检查 WSL 中的 Claude:")
    try:
        # 检查 WSL 是否可用
        wsl_check = subprocess.run(['wsl', '--version'], 
                                 capture_output=True, 
                                 text=True, 
                                 shell=True)
        if wsl_check.returncode == 0:
            print("  ✓ WSL 已安装")
            
            # 在 WSL 中查找 claude
            wsl_result = subprocess.run(['wsl', 'which', 'claude'], 
                                      capture_output=True, 
                                      text=True, 
                                      shell=True)
            if wsl_result.returncode == 0 and wsl_result.stdout.strip():
                wsl_path = wsl_result.stdout.strip()
                print(f"  ✓ WSL 中找到 Claude: {wsl_path}")
                print(f"    可以通过 'wsl claude' 命令调用")
                return 'wsl', wsl_path
        else:
            print("  ✗ WSL 未安装或不可用")
    except Exception as e:
        print(f"  ✗ 检查 WSL 失败: {e}")
    
    return None, None


def main():
    print("Claude CLI 查找工具")
    print("=" * 50)
    
    system = platform.system()
    print(f"当前系统: {system}\n")
    
    if system == 'Windows':
        # 在 Windows 中查找
        claude_path = find_claude_windows()
        
        # 也检查 WSL
        wsl_cmd, wsl_path = check_wsl_claude()
        
        print("\n" + "=" * 50)
        print("总结:")
        
        if claude_path:
            print(f"\n推荐使用 Windows 原生 Claude:")
            print(f"  路径: {claude_path}")
            print(f"\n在 .env 文件中设置:")
            print(f"  CLAUDE_CODE_PATH={claude_path}")
        
        if wsl_path:
            print(f"\n或者使用 WSL 中的 Claude:")
            print(f"  WSL 路径: {wsl_path}")
            print(f"  Windows 调用: wsl claude")
            print(f"\n在 .env 文件中设置:")
            print(f"  CLAUDE_CODE_PATH=wsl")
            print(f"  # 注意：需要修改执行器以支持 WSL 调用")
        
        if not claude_path and not wsl_path:
            print("\n未找到 Claude CLI，请安装：")
            print("\n方法 1 - 通过 npm 安装 (推荐):")
            print("  npm install -g @anthropic/claude-cli")
            print("\n方法 2 - 从 GitHub 下载:")
            print("  https://github.com/anthropics/claude-cli/releases")
            print("\n方法 3 - 在 WSL 中安装:")
            print("  wsl")
            print("  curl -fsSL https://claude.ai/install.sh | sh")
    
    else:
        print("此脚本专为 Windows 环境设计")


if __name__ == '__main__':
    main()