#!/usr/bin/env python3
"""
测试文件系统功能的脚本
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.task_filesystem import TaskFileSystem

def test_filesystem():
    """测试文件系统的基本功能"""
    print("初始化文件系统...")
    task_fs = TaskFileSystem("tasks.db")
    
    print("\n1. 创建项目文件夹...")
    try:
        project = task_fs.create_task_folder(
            parent_path="/",
            name="测试项目",
            description="这是一个测试项目"
        )
        print(f"✓ 创建成功: {project.path}")
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        return
    
    print("\n2. 创建子任务...")
    try:
        task1 = task_fs.create_task_folder(
            parent_path="/测试项目",
            name="功能开发",
            prompt="开发用户登录功能",
            description="实现完整的用户登录系统"
        )
        print(f"✓ 创建成功: {task1.path}")
    except Exception as e:
        print(f"✗ 创建失败: {e}")
    
    print("\n3. 列出目录内容...")
    try:
        items = task_fs.list_directory("/")
        print(f"✓ 根目录包含 {len(items)} 个项目")
        for item in items:
            print(f"  - {item.name} ({item.path})")
    except Exception as e:
        print(f"✗ 列出失败: {e}")
    
    print("\n4. 获取任务树...")
    try:
        tree = task_fs.get_task_tree("/", max_depth=2)
        print(f"✓ 获取成功")
        print(f"  根节点: {tree['name']}")
        if 'children' in tree:
            print(f"  子节点数: {len(tree['children'])}")
    except Exception as e:
        print(f"✗ 获取失败: {e}")
    
    print("\n5. 根据路径查找任务...")
    try:
        task = task_fs.get_task_by_path("/测试项目/功能开发")
        if task:
            print(f"✓ 找到任务: {task.name}")
            print(f"  提示词: {task.prompt}")
        else:
            print("✗ 未找到任务")
    except Exception as e:
        print(f"✗ 查找失败: {e}")
    
    print("\n测试完成！")

if __name__ == '__main__':
    test_filesystem()