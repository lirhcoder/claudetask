-- 文件系统化改造的数据库迁移脚本

-- 1. 在任务表中添加新字段
ALTER TABLE tasks ADD COLUMN task_path TEXT;          -- 完整路径，如: /project1/feature1/subtask1
ALTER TABLE tasks ADD COLUMN task_name TEXT;          -- 任务名称（文件夹名）
ALTER TABLE tasks ADD COLUMN is_folder BOOLEAN DEFAULT 1;  -- 是否是文件夹（任务容器）
ALTER TABLE tasks ADD COLUMN depth INTEGER DEFAULT 0;  -- 嵌套深度
ALTER TABLE tasks ADD COLUMN description TEXT;         -- 详细描述（相当于README）

-- 2. 创建任务文档表（存储任务相关的文档）
CREATE TABLE IF NOT EXISTS task_documents (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    name TEXT NOT NULL,              -- 文档名称
    content TEXT,                    -- 文档内容
    doc_type TEXT DEFAULT 'markdown', -- 文档类型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 3. 创建任务资源表（存储任务生成的文件）
CREATE TABLE IF NOT EXISTS task_resources (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,     -- 'code', 'data', 'output', etc.
    file_path TEXT NOT NULL,         -- 相对于任务的文件路径
    content TEXT,                    -- 文件内容
    metadata TEXT,                   -- JSON格式的元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 4. 添加索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_task_path ON tasks(task_path);
CREATE INDEX IF NOT EXISTS idx_task_parent ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_task_depth ON tasks(depth);
CREATE INDEX IF NOT EXISTS idx_task_documents_task ON task_documents(task_id);
CREATE INDEX IF NOT EXISTS idx_task_resources_task ON task_resources(task_id);

-- 5. 创建视图方便查询
CREATE VIEW IF NOT EXISTS task_tree AS
SELECT 
    t.*,
    p.task_path as parent_path,
    (SELECT COUNT(*) FROM tasks WHERE parent_task_id = t.id) as child_count,
    (SELECT COUNT(*) FROM task_documents WHERE task_id = t.id) as doc_count,
    (SELECT COUNT(*) FROM task_resources WHERE task_id = t.id) as resource_count
FROM tasks t
LEFT JOIN tasks p ON t.parent_task_id = p.id;