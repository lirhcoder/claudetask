#!/usr/bin/env python3
"""
创建默认管理员账户
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import UserManager
import bcrypt

def create_admin():
    """创建默认管理员账户"""
    user_manager = UserManager()
    
    # 检查是否已存在管理员
    admin = user_manager.get_user_by_email('admin@sparticle.com')
    
    if admin:
        print("管理员账户已存在")
        print(f"邮箱: {admin.email}")
        print(f"是否为管理员: {admin.is_admin}")
        
        # 更新密码
        response = input("是否重置密码为 admin123? (y/n): ")
        if response.lower() == 'y':
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            import sqlite3
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET password_hash = ? WHERE email = ?
            ''', (password_hash, 'admin@sparticle.com'))
            conn.commit()
            conn.close()
            print("密码已重置为: admin123")
    else:
        print("创建新的管理员账户...")
        admin = user_manager.create_user(
            email='admin@sparticle.com',
            password='admin123',
            username='admin'
        )
        
        if admin:
            # 设置为管理员
            import sqlite3
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET is_admin = 1 WHERE id = ?
            ''', (admin.id,))
            conn.commit()
            conn.close()
            
            print("管理员账户创建成功！")
            print(f"邮箱: admin@sparticle.com")
            print(f"密码: admin123")
        else:
            print("创建管理员账户失败")

if __name__ == "__main__":
    create_admin()