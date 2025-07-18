#!/usr/bin/env python3
"""
测试登录功能
"""
import sqlite3
import bcrypt
import os

def check_users():
    """检查用户表"""
    db_path = 'tasks.db'
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件 {db_path} 不存在")
        print("\n请先运行: python3 create_admin.py")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查 users 表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ users 表不存在")
            return
        
        # 列出所有用户
        cursor.execute("SELECT id, email, username, is_admin, created_at FROM users")
        users = cursor.fetchall()
        
        print(f"=== 用户列表 ({len(users)} 个用户) ===")
        for user in users:
            admin_tag = "👑 管理员" if user['is_admin'] else "👤 普通用户"
            print(f"\n{admin_tag}")
            print(f"  ID: {user['id']}")
            print(f"  邮箱: {user['email']}")
            print(f"  用户名: {user['username'] or '未设置'}")
            print(f"  创建时间: {user['created_at']}")
        
        if len(users) == 0:
            print("\n❌ 没有找到任何用户")
            print("\n创建默认管理员账号：")
            print("  python3 create_admin.py")
        else:
            print("\n默认管理员账号：")
            print("  邮箱: admin@sparticle.com")
            print("  密码: admin123")
            
            # 测试密码验证
            cursor.execute("SELECT password_hash FROM users WHERE email = ?", ('admin@sparticle.com',))
            admin_user = cursor.fetchone()
            if admin_user:
                # 测试密码
                test_password = 'admin123'
                stored_hash = admin_user['password_hash'].encode('utf-8')
                if bcrypt.checkpw(test_password.encode('utf-8'), stored_hash):
                    print("\n✅ 密码验证成功！")
                else:
                    print("\n❌ 密码验证失败！")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def test_system_config():
    """测试系统配置表"""
    print("\n=== 系统配置表测试 ===")
    
    try:
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(system_config)")
        columns = cursor.fetchall()
        
        if columns:
            print("\nsystem_config 表结构：")
            for col in columns:
                print(f"  {col[1]}: {col[2]}")
        else:
            print("\n❌ system_config 表不存在")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == '__main__':
    check_users()
    test_system_config()