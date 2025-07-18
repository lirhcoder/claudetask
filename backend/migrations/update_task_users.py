"""
迁移脚本：为现有任务更新用户关联
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from pathlib import Path
from models.user import UserManager
from models.task import TaskManager

def main():
    """执行迁移"""
    print("开始迁移任务用户关联...")
    
    # 数据库路径
    db_path = Path(__file__).parent.parent / "tasks.db"
    
    # 获取用户管理器
    user_manager = UserManager()
    
    # 获取所有用户
    users = user_manager.list_users()
    print(f"找到 {len(users)} 个用户")
    
    # 创建邮箱到ID的映射
    email_to_id = {}
    for user in users:
        email_to_id[user.email] = user.id
        print(f"  - {user.email} -> {user.id}")
    
    # 直接操作数据库更新任务
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 检查是否有user_id列
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("tasks表中没有user_id列，跳过迁移")
            return
        
        # 获取所有没有user_id的任务
        cursor.execute("SELECT id, project_path FROM tasks WHERE user_id IS NULL OR user_id = ''")
        tasks_without_user = cursor.fetchall()
        
        print(f"\n找到 {len(tasks_without_user)} 个没有用户关联的任务")
        
        # 尝试从项目路径推断用户
        updated_count = 0
        for task_id, project_path in tasks_without_user:
            # 检查是否有匹配的用户邮箱在路径中
            matched_user_id = None
            
            for email, user_id in email_to_id.items():
                # 简单匹配：如果项目路径包含用户邮箱的一部分
                email_prefix = email.split('@')[0]
                if email_prefix in project_path.lower():
                    matched_user_id = user_id
                    print(f"  任务 {task_id[:8]}... 匹配到用户 {email}")
                    break
            
            if matched_user_id:
                cursor.execute("UPDATE tasks SET user_id = ? WHERE id = ?", (matched_user_id, task_id))
                updated_count += 1
        
        # 对于剩余没有匹配的任务，尝试分配给管理员
        if updated_count < len(tasks_without_user):
            # 查找管理员用户
            admin_user = next((u for u in users if u.email == 'admin@claudetask.local'), None)
            if admin_user:
                print(f"\n将剩余的 {len(tasks_without_user) - updated_count} 个任务分配给管理员")
                cursor.execute("""
                    UPDATE tasks 
                    SET user_id = ? 
                    WHERE (user_id IS NULL OR user_id = '') 
                """, (admin_user.id,))
                updated_count = cursor.rowcount
        
        conn.commit()
        print(f"\n迁移完成！共更新了 {updated_count} 个任务")
        
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        conn.rollback()
        return 1
    finally:
        conn.close()
    
    return 0

if __name__ == '__main__':
    exit(main())