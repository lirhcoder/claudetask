-- 添加 webhook 事件表
CREATE TABLE IF NOT EXISTS webhook_events (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    repository_id TEXT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    payload TEXT,
    processed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_webhook_events_repository ON webhook_events(repository_id);
CREATE INDEX idx_webhook_events_type ON webhook_events(event_type);
CREATE INDEX idx_webhook_events_processed ON webhook_events(processed_at);

-- 在仓库表中添加 webhook 相关字段
ALTER TABLE repositories ADD COLUMN webhook_id TEXT;
ALTER TABLE repositories ADD COLUMN webhook_url TEXT;
ALTER TABLE repositories ADD COLUMN webhook_active BOOLEAN DEFAULT 0;