-- GitHub 风格架构的数据库迁移脚本

-- 1. 仓库表 (原项目表)
CREATE TABLE IF NOT EXISTS repositories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    organization TEXT NOT NULL DEFAULT 'personal',
    description TEXT,
    readme TEXT,
    is_private BOOLEAN DEFAULT FALSE,
    default_branch TEXT DEFAULT 'main',
    github_url TEXT,
    local_path TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- 仓库协作者表
CREATE TABLE IF NOT EXISTS repository_collaborators (
    repository_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT DEFAULT 'developer', -- owner, admin, developer, viewer
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (repository_id, user_id),
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 2. 分支表 (原任务表)
CREATE TABLE IF NOT EXISTS branches (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    repository_id TEXT NOT NULL,
    base_branch TEXT DEFAULT 'main',
    description TEXT,
    status TEXT DEFAULT 'draft', -- draft, in_progress, review, merged, closed
    created_by TEXT NOT NULL,
    assigned_to TEXT,
    pull_request_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);

-- 3. 议题表 (子任务)
CREATE TABLE IF NOT EXISTS issues (
    id TEXT PRIMARY KEY,
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    repository_id TEXT NOT NULL,
    branch_id TEXT,
    status TEXT DEFAULT 'open', -- open, in_progress, resolved, closed
    priority TEXT DEFAULT 'medium', -- low, medium, high, critical
    created_by TEXT NOT NULL,
    assigned_to TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    UNIQUE (repository_id, number)
);

-- 议题标签表
CREATE TABLE IF NOT EXISTS issue_labels (
    issue_id TEXT NOT NULL,
    label TEXT NOT NULL,
    color TEXT DEFAULT '#0366d6',
    PRIMARY KEY (issue_id, label),
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE
);

-- 4. 提交表 (执行记录)
CREATE TABLE IF NOT EXISTS commits (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL,
    message TEXT NOT NULL,
    description TEXT,
    author_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_generated BOOLEAN DEFAULT TRUE,
    files_changed TEXT, -- JSON 数组
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- 5. 评论表
CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    issue_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- 6. Pull Request 表
CREATE TABLE IF NOT EXISTS pull_requests (
    id TEXT PRIMARY KEY,
    number INTEGER NOT NULL,
    repository_id TEXT NOT NULL,
    branch_id TEXT NOT NULL,
    target_branch TEXT DEFAULT 'main',
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open', -- open, merged, closed
    created_by TEXT NOT NULL,
    merged_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    merged_at TIMESTAMP,
    closed_at TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (merged_by) REFERENCES users(id),
    UNIQUE (repository_id, number)
);

-- 7. GitHub 同步状态表
CREATE TABLE IF NOT EXISTS github_sync_status (
    repository_id TEXT PRIMARY KEY,
    last_sync_at TIMESTAMP,
    sync_status TEXT DEFAULT 'pending', -- pending, syncing, success, failed
    error_message TEXT,
    github_stars INTEGER DEFAULT 0,
    github_forks INTEGER DEFAULT 0,
    github_issues INTEGER DEFAULT 0,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_branches_repository ON branches(repository_id);
CREATE INDEX IF NOT EXISTS idx_branches_status ON branches(status);
CREATE INDEX IF NOT EXISTS idx_issues_repository ON issues(repository_id);
CREATE INDEX IF NOT EXISTS idx_issues_branch ON issues(branch_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_commits_branch ON commits(branch_id);
CREATE INDEX IF NOT EXISTS idx_comments_issue ON comments(issue_id);
CREATE INDEX IF NOT EXISTS idx_pull_requests_repository ON pull_requests(repository_id);
CREATE INDEX IF NOT EXISTS idx_pull_requests_branch ON pull_requests(branch_id);

-- 创建序列号生成器视图（用于议题和 PR 编号）
CREATE VIEW IF NOT EXISTS next_issue_number AS
SELECT r.id as repository_id, 
       COALESCE(MAX(i.number), 0) + 1 as next_number
FROM repositories r
LEFT JOIN issues i ON r.id = i.repository_id
GROUP BY r.id;

CREATE VIEW IF NOT EXISTS next_pr_number AS
SELECT r.id as repository_id, 
       COALESCE(MAX(pr.number), 0) + 1 as next_number
FROM repositories r
LEFT JOIN pull_requests pr ON r.id = pr.repository_id
GROUP BY r.id;