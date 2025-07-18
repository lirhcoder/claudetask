"""
从任务中自动创建用户
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from pathlib import Path
from models.user import UserManager
import re

def extract_email_from_path(project_path):
    """从项目路径中提取可能的邮箱"""
    # 寻找类似 rh-li-0718-001 或 rh.li@sparticle.com 的模式
    
    # 模式1: 查找邮箱格式
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email_match = re.search(email_pattern, project_path)
    if email_match:
        return email_match.group(0)
    
    # 模式2: 从项目名称推断 (如 rh-li-0718-001 -> rh.li)
    path_parts = project_path.split('/')
    project_name = path_parts[-1] if path_parts else ''
    
    # 匹配类似 xx-yy-数字-数字 的格式
    name_pattern = r'^([a-zA-Z]+)-([a-zA-Z]+)-\d+'
    name_match = re.match(name_pattern, project_name)
    if name_match:
        first_part = name_match.group(1).lower()
        second_part = name_match.group(2).lower()
        # 尝试构造邮箱（这里需要域名信息）
        possible_email = f"{first_part}.{second_part}"
        return possible_email
    
    return None

def main():
    """执行迁移"""
    print("开始从任务中自动创建用户...")
    
    # 数据库路径
    db_path = Path(__file__).parent.parent / "tasks.db"
    
    # 获取用户管理器
    user_manager = UserManager()
    
    # 获取系统配置
    config = user_manager.get_system_config()
    default_domain = config.allowed_email_domain or '@sparticle.com'  # 默认域名
    if not default_domain.startswith('@'):
        default_domain = '@' + default_domain
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 获取所有唯一的user_id
        cursor.execute("""
            SELECT DISTINCT user_id 
            FROM tasks 
            WHERE user_id IS NOT NULL AND user_id != ''
        """)
        task_user_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"找到 {len(task_user_ids)} 个唯一的任务用户ID")
        
        # 获取现有用户ID
        existing_users = user_manager.list_users()
        existing_user_ids = {user.id for user in existing_users}
        existing_emails = {user.email for user in existing_users}
        
        # 找出需要创建的用户
        new_user_ids = [uid for uid in task_user_ids if uid not in existing_user_ids]
        print(f"需要创建 {len(new_user_ids)} 个新用户")
        
        created_count = 0
        
        for user_id in new_user_ids:
            # 获取该用户的任务信息
            cursor.execute("""
                SELECT project_path, COUNT(*) as task_count
                FROM tasks 
                WHERE user_id = ?
                GROUP BY project_path
                ORDER BY task_count DESC
                LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                project_path = result[0]
                
                # 尝试从路径提取邮箱信息
                email_hint = extract_email_from_path(project_path)
                
                if email_hint and '@' in email_hint:
                    # 完整邮箱
                    email = email_hint
                elif email_hint:
                    # 只有用户名部分，添加域名
                    email = email_hint + default_domain
                else:
                    # 无法推断，使用user_id的前8位
                    email = user_id[:8] + default_domain
                
                # 确保邮箱唯一
                base_email = email
                counter = 1
                while email in existing_emails:
                    name_part = base_email.split('@')[0]
                    domain_part = base_email.split('@')[1]
                    email = f"{name_part}{counter}@{domain_part}"
                    counter += 1
                
                # 创建用户
                print(f"  创建用户: {email} (ID: {user_id})")
                
                # 直接插入数据库，保持原有的user_id
                cursor.execute("""
                    INSERT INTO users (id, email, username, password_hash, is_admin, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (
                    user_id,
                    email,
                    email.split('@')[0],
                    '',  # 空密码，需要用户重置
                    0,   # 非管理员
                ))
                
                existing_emails.add(email)
                created_count += 1
        
        conn.commit()
        print(f"\n迁移完成！共创建了 {created_count} 个用户")
        
        # 显示创建的用户
        if created_count > 0:
            print("\n新创建的用户需要：")
            print("1. 管理员设置密码")
            print("2. 或通过'忘记密码'功能重置")
        
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        conn.rollback()
        return 1
    finally:
        conn.close()
    
    return 0

if __name__ == '__main__':
    exit(main())