"""
检查特定用户的任务
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from pathlib import Path
from models.user import UserManager

def main():
    """检查用户任务"""
    db_path = Path(__file__).parent / "tasks.db"
    
    # 获取用户管理器
    user_manager = UserManager()
    
    # 查找用户
    target_email = "rh.li@sparticle.com"
    user = user_manager.get_user_by_email(target_email)
    
    if user:
        print(f"找到用户: {user.email} (ID: {user.id})")
    else:
        print(f"未找到用户: {target_email}")
        # 列出所有用户
        print("\n所有用户:")
        for u in user_manager.list_users():
            print(f"  - {u.email} (ID: {u.id})")
        return
    
    # 查询该用户的任务
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 统计任务的user_id情况
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id IS NULL OR user_id = ''")
    no_user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM tasks WHERE user_id IS NOT NULL AND user_id != ''")
    unique_users = cursor.fetchone()[0]
    
    print(f"\n任务统计:")
    print(f"  - 没有user_id的任务: {no_user_count}")
    print(f"  - 唯一的user_id数: {unique_users}")
    
    # 查询所有任务
    cursor.execute("SELECT id, user_id, project_path, created_at FROM tasks ORDER BY created_at DESC LIMIT 20")
    all_tasks = cursor.fetchall()
    
    print(f"\n最近20个任务:")
    for task_id, task_user_id, project_path, created_at in all_tasks:
        user_info = "无用户" if not task_user_id else task_user_id[:8]
        print(f"  - {task_id[:8]}... user_id={user_info} path={project_path}")
    
    # 查找包含 rh-li 或 rh.li 的任务
    cursor.execute("SELECT id, user_id, project_path FROM tasks WHERE project_path LIKE '%rh-li%' OR project_path LIKE '%rh.li%'")
    rh_tasks = cursor.fetchall()
    
    if rh_tasks:
        print(f"\n找到 {len(rh_tasks)} 个包含 rh-li/rh.li 的任务:")
        for task_id, task_user_id, project_path in rh_tasks[:5]:
            user_info = "无用户" if not task_user_id else task_user_id
            print(f"  - {task_id[:8]}... user_id={user_info}")
            print(f"    path: {project_path}")
    
    # 查询特定用户的任务
    if user:
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user.id,))
        count = cursor.fetchone()[0]
        print(f"\n用户 {user.email} 的任务数: {count}")
    
    conn.close()

if __name__ == '__main__':
    main()