#!/usr/bin/env python3
"""
调试路径问题的脚本
"""
import os
from pathlib import Path

def test_project_path():
    """测试项目路径"""
    # 测试路径
    test_paths = [
        "./projects/claude-task-0717-001",
        "projects/claude-task-0717-001",
        "/mnt/c/development/claudetask/projects/claude-task-0717-001",
        "C:\\development\\claudetask\\projects\\claude-task-0717-001",
        os.path.join(os.getcwd(), "projects", "claude-task-0717-001")
    ]
    
    print("当前工作目录:", os.getcwd())
    print("=" * 60)
    
    for test_path in test_paths:
        print(f"\n测试路径: {test_path}")
        print("-" * 40)
        
        # 转换 Windows 路径
        if '\\' in test_path:
            if len(test_path) > 2 and test_path[1:3] == ':\\':
                drive_letter = test_path[0].lower()
                path_part = test_path[3:].replace('\\', '/')
                converted_path = f'/mnt/{drive_letter}/{path_part}'
                print(f"Windows 路径转换: {converted_path}")
                test_path = converted_path
        
        try:
            path = Path(test_path)
            print(f"Path 对象: {path}")
            print(f"绝对路径: {path.absolute()}")
            print(f"是否存在: {path.exists()}")
            print(f"是否是目录: {path.is_dir() if path.exists() else 'N/A'}")
            print(f"是否是绝对路径: {path.is_absolute()}")
            
            if path.exists():
                print(f"规范路径: {path.resolve()}")
                
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    # 创建测试项目目录
    test_project = Path("./projects/claude-task-0717-001")
    test_project.mkdir(parents=True, exist_ok=True)
    print(f"创建测试目录: {test_project.absolute()}")
    
    # 测试路径
    test_project_path()