-- 备份旧表（如果存在）
DROP TABLE IF EXISTS system_config_old;
ALTER TABLE system_config RENAME TO system_config_old;

-- 创建新的系统配置表
CREATE TABLE system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    type TEXT DEFAULT 'string',
    description TEXT,
    category TEXT DEFAULT 'general',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);