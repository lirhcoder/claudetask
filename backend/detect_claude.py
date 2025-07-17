#!/usr/bin/env python3
"""
检测 Claude Code CLI 安装位置
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def detect_claude():
    """检测 Claude 命令的位置"""
    results = {
        'found': False,
        'path': None,
        'version': None,
        'install_instructions': 'npm install -g @anthropic-ai/claude-code'
    }
    
    # 方法1: 直接调用
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            results['found'] = True
            results['path'] = 'claude'
            results['version'] = result.stdout.strip()
            return results
    except FileNotFoundError:
        pass
    
    # 方法2: 使用 where/which
    try:
        if sys.platform == 'win32':
            result = subprocess.run(['where', 'claude'], capture_output=True, text=True)
        else:
            result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            claude_path = result.stdout.strip().split('\n')[0]
            results['found'] = True
            results['path'] = claude_path
            
            # 获取版本
            try:
                ver_result = subprocess.run([claude_path, '--version'], capture_output=True, text=True)
                results['version'] = ver_result.stdout.strip()
            except:
                pass
            
            return results
    except:
        pass
    
    # 方法3: Windows 常见位置
    if sys.platform == 'win32':
        common_paths = [
            r'C:\Program Files\Claude\claude.exe',
            r'C:\Program Files (x86)\Claude\claude.exe',
            os.path.expanduser(r'~\AppData\Local\Programs\claude\claude.exe'),
            os.path.expanduser(r'~\AppData\Roaming\npm\claude.cmd'),
            os.path.expanduser(r'~\AppData\Roaming\npm\claude.ps1'),
            os.path.expanduser(r'~\AppData\Roaming\npm\node_modules\.bin\claude.cmd'),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                results['found'] = True
                results['path'] = path
                
                # 获取版本
                try:
                    ver_result = subprocess.run([path, '--version'], capture_output=True, text=True, shell=True)
                    results['version'] = ver_result.stdout.strip()
                except:
                    pass
                
                return results
    
    # 方法4: 检查 npm 全局包
    try:
        npm_result = subprocess.run(['npm', 'list', '-g', '@anthropic-ai/claude-code'], 
                                  capture_output=True, text=True)
        if '@anthropic-ai/claude-code' in npm_result.stdout:
            results['found'] = True
            results['path'] = 'npx @anthropic-ai/claude-code'
            results['version'] = 'via npx'
            return results
    except:
        pass
    
    return results

def write_env_file(claude_path):
    """写入 .env 文件"""
    env_file = Path('.env.local')
    
    # 读取现有内容
    existing_lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            existing_lines = [line.strip() for line in f.readlines() 
                            if line.strip() and not line.startswith('CLAUDE_PATH=')]
    
    # 添加 CLAUDE_PATH
    existing_lines.append(f'CLAUDE_PATH={claude_path}')
    
    # 写入文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(existing_lines) + '\n')
    
    print(f"已将 CLAUDE_PATH 写入 {env_file}")

def main():
    print("检测 Claude Code CLI...")
    print("-" * 50)
    
    result = detect_claude()
    
    if result['found']:
        print(f"✅ 找到 Claude Code CLI")
        print(f"   路径: {result['path']}")
        if result['version']:
            print(f"   版本: {result['version']}")
        
        # 询问是否保存到环境变量
        if input("\n是否将此路径保存到 .env.local 文件？(y/n): ").lower() == 'y':
            write_env_file(result['path'])
    else:
        print("❌ 未找到 Claude Code CLI")
        print(f"\n安装方法: {result['install_instructions']}")
        print("\n如果已安装但未找到，请手动设置环境变量 CLAUDE_PATH")
    
    # 输出 JSON 结果（供其他程序使用）
    print("\n" + "-" * 50)
    print("JSON 结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()