#!/usr/bin/env python3
"""
修复 Windows 环境中的数据库兼容性问题
"""
import sqlite3
import os
import sys

def fix_system_config_table(db_path='tasks.db'):
    """修复 system_config 表的兼容性问题"""
    print(f"修复数据库: {os.path.abspath(db_path)}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 检查旧的 system_config 表结构
        cursor.execute("PRAGMA table_info(system_config)")
        old_columns = cursor.fetchall()
        old_column_names = [col[1] for col in old_columns]
        
        print(f"当前列: {old_column_names}")
        
        # 2. 如果是旧结构，需要迁移
        if 'allowed_email_domain' in old_column_names:
            print("检测到旧的 system_config 表结构，开始迁移...")
            
            # 备份旧数据
            cursor.execute("""
                SELECT id, allowed_email_domain, require_email_verification, super_admin_email 
                FROM system_config LIMIT 1
            """)
            old_data = cursor.fetchone()
            
            # 删除旧表
            cursor.execute("DROP TABLE IF EXISTS system_config")
            
            # 创建新表（配置管理系统使用的结构）
            cursor.execute("""
                CREATE TABLE system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    type TEXT DEFAULT 'string',
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                )
            """)
            
            # 如果有旧数据，迁移到新格式
            if old_data:
                configs_to_insert = [
                    ('auth.allowed_email_domain', old_data[1] or '@sparticle.com', 'string', 
                     '允许的邮箱域名', 'auth', 'migration'),
                    ('auth.require_email_verification', 'true' if old_data[2] else 'false', 
                     'boolean', '是否需要邮箱验证', 'auth', 'migration'),
                    ('auth.super_admin_email', old_data[3] or 'admin@sparticle.com', 
                     'string', '超级管理员邮箱', 'auth', 'migration')
                ]
                
                for config in configs_to_insert:
                    cursor.execute("""
                        INSERT INTO system_config (key, value, type, description, category, updated_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, config)
                
                print("✅ 已迁移旧配置到新格式")
            
            print("✅ system_config 表已更新为新结构")
            
        elif 'key' in old_column_names and 'value' in old_column_names:
            print("✅ system_config 表结构正确")
        else:
            print("❌ 未知的表结构，创建新表...")
            cursor.execute("DROP TABLE IF EXISTS system_config")
            cursor.execute("""
                CREATE TABLE system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    type TEXT DEFAULT 'string',
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                )
            """)
            print("✅ 创建了新的 system_config 表")
        
        # 3. 确保必要的配置存在
        cursor.execute("SELECT COUNT(*) FROM system_config WHERE key = 'auth.allowed_email_domain'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO system_config (key, value, type, description, category, updated_by)
                VALUES ('auth.allowed_email_domain', '@sparticle.com', 'string', 
                        '允许的邮箱域名', 'auth', 'system')
            """)
            print("✅ 添加了默认邮箱域名配置")
        
        conn.commit()
        conn.close()
        
        print("\n✅ 数据库修复完成！")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_user_model():
    """更新 user.py 以兼容新的配置系统"""
    print("\n建议更新 models/user.py 中的 get_system_config 方法")
    print("使用以下代码替换:")
    print("-" * 60)
    print("""
def get_system_config(self) -> SystemConfig:
    '''获取系统配置'''
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        # 尝试新的配置系统
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_config'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(system_config)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # 新的配置系统（key-value 格式）
            if 'key' in columns:
                cursor.execute('''
                    SELECT key, value FROM system_config 
                    WHERE key IN ('auth.allowed_email_domain', 
                                  'auth.require_email_verification', 
                                  'auth.super_admin_email')
                ''')
                
                config_dict = {row[0]: row[1] for row in cursor.fetchall()}
                
                return SystemConfig(
                    id='default',
                    allowed_email_domain=config_dict.get('auth.allowed_email_domain', '@sparticle.com'),
                    require_email_verification=config_dict.get('auth.require_email_verification', 'false').lower() == 'true',
                    super_admin_email=config_dict.get('auth.super_admin_email', 'admin@sparticle.com')
                )
            # 旧的配置系统
            else:
                cursor.execute('SELECT * FROM system_config LIMIT 1')
                row = cursor.fetchone()
                if row:
                    return SystemConfig(
                        id=row[0],
                        allowed_email_domain=row[1],
                        require_email_verification=bool(row[2]),
                        super_admin_email=row[3]
                    )
        
        # 返回默认配置
        return SystemConfig(
            id='default',
            allowed_email_domain='@sparticle.com',
            require_email_verification=False,
            super_admin_email='admin@sparticle.com'
        )
    """)
    print("-" * 60)

if __name__ == '__main__':
    # 支持指定数据库路径
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'tasks.db'
    
    if fix_system_config_table(db_path):
        update_user_model()
        print("\n现在可以重新启动 Flask 应用了！")