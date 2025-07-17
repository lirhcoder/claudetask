#!/usr/bin/env python3
"""
Claude 任务执行器 - 捕获输出并上传结果
"""
import sys
import os
import subprocess
import time
import signal
import json
import argparse
from pathlib import Path
from datetime import datetime

# 设置编码
if sys.platform == 'win32':
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

# 解析命令行参数
parser = argparse.ArgumentParser(description='Claude 任务执行器')
parser.add_argument('--task-id', required=True, help='任务ID')
parser.add_argument('--prompt-file', help='包含提示词的文件路径')
parser.add_argument('--prompt', help='直接提供的提示词')
parser.add_argument('--project-path', required=True, help='项目路径')
parser.add_argument('--base-url', default='http://localhost:5000', help='API服务器地址')

# 兼容旧的位置参数格式
if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
    # 旧格式: claude_executor.py <task_id> <prompt> <project_path> [base_url]
    if len(sys.argv) < 4:
        print("用法: claude_executor.py <task_id> <prompt> <project_path> [base_url]")
        sys.exit(1)
    task_id = sys.argv[1]
    prompt = sys.argv[2]
    project_path = sys.argv[3]
    base_url = sys.argv[4] if len(sys.argv) > 4 else "http://localhost:5000"
else:
    # 新格式: 使用 argparse
    args = parser.parse_args()
    task_id = args.task_id
    project_path = args.project_path
    base_url = args.base_url
    
    # 获取提示词
    if args.prompt_file:
        try:
            with open(args.prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
        except Exception as e:
            print(f"读取提示词文件失败: {e}")
            sys.exit(1)
    elif args.prompt:
        prompt = args.prompt
    else:
        print("错误: 必须提供 --prompt 或 --prompt-file")
        sys.exit(1)

# 设置工作目录
os.chdir(project_path)
print(f"工作目录: {os.getcwd()}")

# 创建输出文件
temp_dir = Path(__file__).parent / "temp"
temp_dir.mkdir(exist_ok=True)
output_file = temp_dir / f"task_{task_id}_output.txt"
result_file = temp_dir / f"task_{task_id}_result.json"

# 设置信号处理
interrupted = False
exit_code = None

def signal_handler(signum, frame):
    global interrupted
    interrupted = True
    print("\n任务被用户中断")
    # 不立即退出，让进程清理

signal.signal(signal.SIGINT, signal_handler)
if hasattr(signal, 'SIGTERM'):
    signal.signal(signal.SIGTERM, signal_handler)

# 执行 Claude
start_time = time.time()
process = None

try:
    print("\n正在执行 Claude Code...")
    print("-" * 60)
    
    # 打开输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入头部信息
        f.write(f"Task ID: {task_id}\n")
        f.write(f"Started: {datetime.now().isoformat()}\n")
        f.write(f"Project: {project_path}\n")
        f.write(f"Prompt: {prompt}\n")
        f.write("-" * 60 + "\n\n")
        f.flush()
        
        # 查找 claude 命令
        claude_cmd = None
        
        # 方法0: 检查环境变量
        claude_path_env = os.environ.get('CLAUDE_PATH')
        if claude_path_env and os.path.exists(claude_path_env):
            claude_cmd = [claude_path_env, prompt]
            print(f"使用环境变量 CLAUDE_PATH: {claude_path_env}")
        
        # 方法1: 尝试直接使用 claude
        if not claude_cmd:
            try:
                # 在 Windows 上使用 shell 来执行可能的批处理文件
                if sys.platform == 'win32':
                    result = subprocess.run(['claude', '--version'], 
                                          capture_output=True, 
                                          check=False, 
                                          shell=True)
                else:
                    result = subprocess.run(['claude', '--version'], 
                                          capture_output=True, 
                                          check=False)
                
                if result.returncode == 0:
                    claude_cmd = ['claude', prompt]
                    print("找到 claude 命令（通过 PATH）")
            except Exception:
                pass
        
        # 方法2: 尝试使用 where/which 查找
        if not claude_cmd:
            try:
                if sys.platform == 'win32':
                    result = subprocess.run(['where', 'claude'], capture_output=True, text=True, check=False)
                else:
                    result = subprocess.run(['which', 'claude'], capture_output=True, text=True, check=False)
                
                if result.returncode == 0 and result.stdout.strip():
                    claude_path = result.stdout.strip().split('\n')[0]
                    claude_cmd = [claude_path, prompt]
            except:
                pass
        
        # 方法3: 检查常见安装位置
        if not claude_cmd and sys.platform == 'win32':
            common_paths = [
                r'C:\Program Files\Claude\claude.exe',
                r'C:\Program Files (x86)\Claude\claude.exe',
                os.path.expanduser(r'~\AppData\Local\Programs\claude\claude.exe'),
                os.path.expanduser(r'~\AppData\Roaming\npm\claude.cmd'),
                os.path.expanduser(r'~\AppData\Roaming\npm\claude.ps1'),
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    claude_cmd = [path, prompt]
                    break
        
        # 方法4: 尝试使用 npx
        if not claude_cmd:
            try:
                subprocess.run(['npx', '--version'], capture_output=True, check=False)
                claude_cmd = ['npx', '@anthropic-ai/claude-code', prompt]
            except FileNotFoundError:
                pass
        
        if not claude_cmd:
            raise FileNotFoundError(
                "找不到 Claude 命令。请确保已安装 Claude Code CLI。\n"
                "安装方法: npm install -g @anthropic-ai/claude-code"
            )
        
        print(f"使用命令: {' '.join(claude_cmd[:2])}...")
        
        # 判断是否需要使用 shell
        use_shell = False
        if sys.platform == 'win32':
            # Windows 下，.cmd, .bat, .ps1 文件需要使用 shell
            cmd_path = claude_cmd[0].lower()
            if cmd_path.endswith(('.cmd', '.bat', '.ps1')):
                use_shell = True
                print(f"Windows 脚本文件，使用 shell 执行")
            elif cmd_path == 'claude':
                # 如果是 'claude' 命令且在 Windows 上，也使用 shell
                # 因为它可能是通过 npm 安装的批处理包装器
                use_shell = True
                print(f"Windows 上的 claude 命令，使用 shell 执行")
        
        # 执行 Claude
        process = subprocess.Popen(
            claude_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            shell=use_shell
        )
        
        # 实时捕获输出
        for line in process.stdout:
            if interrupted:
                process.terminate()
                break
            print(line, end='')
            f.write(line)
            f.flush()
        
        # 等待进程结束
        process.wait()
        exit_code = process.returncode
        
        # 写入尾部信息
        f.write(f"\n\n{'-' * 60}\n")
        f.write(f"Completed: {datetime.now().isoformat()}\n")
        f.write(f"Exit Code: {exit_code}\n")
        f.write(f"Interrupted: {interrupted}\n")
        
except Exception as e:
    print(f"\n执行出错: {e}")
    exit_code = 1
    
    # 记录错误
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\nError: {str(e)}\n")

finally:
    # 确保进程结束
    if process and process.poll() is None:
        process.terminate()
        process.wait()
    
    duration = time.time() - start_time
    print(f"\n执行时间: {duration:.2f} 秒")

# 创建结果数据
result_data = {
    'task_id': task_id,
    'completed_at': datetime.now().isoformat(),
    'exit_code': exit_code or -1,
    'duration': duration,
    'interrupted': interrupted,
    'status': 'cancelled' if interrupted else ('completed' if exit_code == 0 else 'failed'),
    'output': ''
}

# 读取输出内容
if output_file.exists():
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            result_data['output'] = f.read()
    except:
        result_data['output'] = "无法读取输出文件"

# 保存结果文件
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result_data, f, ensure_ascii=False, indent=2)

print(f"\n结果已保存到: {result_file}")

# 尝试上传结果
try:
    # 添加当前目录到 Python 路径
    sys.path.insert(0, str(Path(__file__).parent))
    from services.result_uploader import upload_task_result
    
    print("\n正在上传执行结果...")
    success = upload_task_result(
        task_id=task_id,
        output_file=output_file,
        exit_code=exit_code or -1,
        duration=duration,
        interrupted=interrupted,
        base_url=base_url
    )
    
    if success:
        print("✅ 执行结果已上传到服务器")
    else:
        print("❌ 上传失败，结果保存在本地")
        
except Exception as e:
    print(f"❌ 上传出错: {e}")
    print(f"结果文件保存在: {result_file}")

# 清理临时文件（可选）
# output_file.unlink()

sys.exit(exit_code or 0)