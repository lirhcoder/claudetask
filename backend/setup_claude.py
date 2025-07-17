#!/usr/bin/env python3
"""
设置 Claude CLI 路径的辅助脚本
"""
import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.claude_detector import detect_claude_path, get_environment_info, create_environment_config


def main():
    print("Claude Code 环境检测工具")
    print("=" * 50)
    
    # 获取环境信息
    env_info = get_environment_info()
    config = create_environment_config()
    
    print(f"\n当前环境:")
    print(f"  系统: {env_info['system']}")
    print(f"  版本: {env_info['release']}")
    print(f"  Python: {env_info['python_version']}")
    if env_info['is_wsl']:
        print("  环境: WSL (Windows Subsystem for Linux)")
    if env_info['is_docker']:
        print("  环境: Docker 容器")
    
    print(f"\nClaude CLI 检测结果:")
    if config['claude_path']:
        print(f"  ✓ 找到 Claude: {config['claude_path']}")
        
        # 测试执行
        try:
            import subprocess
            result = subprocess.run([config['claude_path'], '--version'], 
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"  ✓ Claude 版本: {result.stdout.strip()}")
            else:
                print(f"  ⚠ Claude 可能无法正常执行")
        except Exception as e:
            print(f"  ⚠ 无法执行 Claude: {e}")
    else:
        print("  ✗ 未找到 Claude CLI")
        print("\n建议:")
        for rec in config['recommendations']:
            print(f"  - {rec}")
    
    # 生成配置建议
    print(f"\n配置文件建议:")
    
    env_file = '.env'
    if env_info['is_wsl']:
        env_file = '.env.wsl'
        print(f"  检测到 WSL 环境，建议使用 {env_file}")
    
    # 检查配置文件
    if os.path.exists(env_file):
        print(f"  {env_file} 已存在")
        
        # 读取当前配置
        current_claude_path = None
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip().startswith('CLAUDE_CODE_PATH='):
                    current_claude_path = line.strip().split('=', 1)[1]
                    break
        
        if current_claude_path:
            print(f"  当前配置的 Claude 路径: {current_claude_path}")
            if not os.path.exists(current_claude_path):
                print(f"  ⚠ 警告: 配置的路径不存在!")
    else:
        print(f"  {env_file} 不存在")
        
        # 提供创建建议
        if config['claude_path']:
            print(f"\n  建议在 {env_file} 中添加:")
            print(f"  CLAUDE_CODE_PATH={config['claude_path']}")
        else:
            print(f"\n  请安装 Claude CLI 后重新运行此脚本")
            print(f"  或手动在 {env_file} 中设置 CLAUDE_CODE_PATH")
    
    # 如果没找到 Claude，提供手动输入选项
    claude_path = config['claude_path']
    if not claude_path:
        print(f"\n是否手动指定 Claude CLI 路径? (y/N): ", end='')
        response = input().strip().lower()
        
        if response == 'y':
            print("\n常见的 Claude 安装位置:")
            if env_info['system'] == 'Windows':
                print("  - C:\\Users\\<用户名>\\AppData\\Local\\Programs\\claude\\claude.exe")
                print("  - C:\\Program Files\\claude\\claude.exe")
                print("  - C:\\Users\\<用户名>\\.claude\\bin\\claude.exe")
            elif env_info['is_wsl']:
                print("  - /usr/local/bin/claude")
                print("  - ~/.local/bin/claude")
                print("  - /mnt/c/Users/<用户名>/AppData/Local/Programs/claude/claude.exe (Windows 版本)")
            else:
                print("  - /usr/local/bin/claude")
                print("  - ~/.local/bin/claude")
                print("  - ~/bin/claude")
            
            print("\n请输入 Claude CLI 的完整路径: ", end='')
            manual_path = input().strip()
            
            # 验证路径
            if manual_path and os.path.exists(manual_path):
                claude_path = manual_path
                print(f"  ✓ 找到 Claude: {claude_path}")
                
                # 测试执行
                try:
                    import subprocess
                    result = subprocess.run([claude_path, '--version'], 
                                            capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        print(f"  ✓ Claude 版本: {result.stdout.strip()}")
                    else:
                        print(f"  ⚠ Claude 可能无法正常执行")
                except Exception as e:
                    print(f"  ⚠ 无法执行 Claude: {e}")
            else:
                print(f"  ✗ 路径不存在: {manual_path}")
    
    # 更新 .env 文件
    if claude_path and os.path.exists(env_file):
        print(f"\n是否更新 {env_file} 中的 CLAUDE_CODE_PATH? (y/N): ", end='')
        response = input().strip().lower()
        
        if response == 'y':
            # 读取现有配置
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # 查找并更新 CLAUDE_CODE_PATH
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith('CLAUDE_CODE_PATH=') or line.strip().startswith('#CLAUDE_CODE_PATH='):
                    lines[i] = f'CLAUDE_CODE_PATH={claude_path}\n'
                    updated = True
                    break
            
            # 如果没找到，添加到文件末尾
            if not updated:
                # 在 Claude Code Configuration 部分后添加
                for i, line in enumerate(lines):
                    if 'Claude Code Configuration' in line:
                        # 找到下一个空行或注释行
                        j = i + 1
                        while j < len(lines) and (lines[j].strip().startswith('#') or lines[j].strip()):
                            j += 1
                        lines.insert(j, f'CLAUDE_CODE_PATH={claude_path}\n')
                        updated = True
                        break
                
                if not updated:
                    lines.append(f'\nCLAUDE_CODE_PATH={claude_path}\n')
            
            # 写回文件
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            print(f"  ✓ 已更新 {env_file}")
            print(f"  ✓ Claude 路径已设置为: {claude_path}")
    
    # 提供自动创建选项
    elif claude_path and not os.path.exists(env_file):
        print(f"\n是否自动创建 {env_file} 文件? (y/N): ", end='')
        response = input().strip().lower()
        
        if response == 'y':
            # 复制示例文件
            example_file = f"{env_file}.example"
            if os.path.exists(example_file):
                with open(example_file, 'r') as f:
                    content = f.read()
                
                # 替换 Claude 路径
                content = content.replace(
                    '# CLAUDE_CODE_PATH=C:/Users/YourName/AppData/Local/Programs/claude/claude.exe',
                    f'CLAUDE_CODE_PATH={claude_path}'
                )
                
                with open(env_file, 'w') as f:
                    f.write(content)
                
                print(f"  ✓ 已创建 {env_file}")
                print(f"  ✓ Claude 路径已设置为: {claude_path}")
            else:
                print(f"  ✗ 找不到 {example_file}")


if __name__ == '__main__':
    main()