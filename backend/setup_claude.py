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
    else:
        print(f"  {env_file} 不存在")
        
        # 提供创建建议
        if config['claude_path']:
            print(f"\n  建议在 {env_file} 中添加:")
            print(f"  CLAUDE_CODE_PATH={config['claude_path']}")
        else:
            print(f"\n  请安装 Claude CLI 后重新运行此脚本")
            print(f"  或手动在 {env_file} 中设置 CLAUDE_CODE_PATH")
    
    # 提供自动创建选项
    if not os.path.exists(env_file) and config['claude_path']:
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
                    '# CLAUDE_CODE_PATH=/home/username/.local/bin/claude',
                    f'CLAUDE_CODE_PATH={config["claude_path"]}'
                )
                
                with open(env_file, 'w') as f:
                    f.write(content)
                
                print(f"  ✓ 已创建 {env_file}")
                print(f"  ✓ Claude 路径已设置为: {config['claude_path']}")
            else:
                print(f"  ✗ 找不到 {example_file}")


if __name__ == '__main__':
    main()