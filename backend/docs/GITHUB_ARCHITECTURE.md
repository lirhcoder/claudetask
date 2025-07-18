# GitHub 风格的项目任务管理架构设计

## 概念映射

### 传统 ClaudeTask → GitHub 模式
- **Project (项目)** → **Repository (仓库)**
- **Task (任务)** → **Branch (分支)** 
- **Sub-task (子任务)** → **Issue/PR (议题/拉取请求)**
- **Task Description** → **README.md / Issue Description**
- **Task Execution** → **Commit & Push**

## 文件系统结构

```
/workspace
├── /organizations (组织)
│   ├── /sparticle
│   │   ├── /repositories (仓库)
│   │   │   ├── /claudetask
│   │   │   │   ├── .git/
│   │   │   │   ├── README.md
│   │   │   │   ├── /branches (分支/任务)
│   │   │   │   │   ├── /main
│   │   │   │   │   │   ├── status.json
│   │   │   │   │   │   └── commits.log
│   │   │   │   │   ├── /feature/add-login
│   │   │   │   │   │   ├── README.md (任务描述)
│   │   │   │   │   │   ├── status.json
│   │   │   │   │   │   ├── commits.log
│   │   │   │   │   │   └── /issues (子任务)
│   │   │   │   │   │       ├── /issue-1-ui-design
│   │   │   │   │   │       │   ├── description.md
│   │   │   │   │   │       │   ├── comments.json
│   │   │   │   │   │       │   └── status.json
│   │   │   │   │   │       └── /issue-2-backend-api
│   │   │   │   │   └── /bugfix/fix-memory-leak
│   │   │   │   └── /pull-requests
│   │   │   │       └── /pr-123
│   │   │   │           ├── description.md
│   │   │   │           ├── diff.patch
│   │   │   │           └── review.json
│   │   │   └── /another-project
│   │   └── /teams
│   │       └── /development
│   └── /personal (个人仓库)
│       └── /user@email.com
│           └── /repositories
└── /templates (模板)
    ├── /project-templates
    └── /task-templates
```

## 数据模型设计

### 1. Repository (仓库) - 原 Project
```python
class Repository:
    id: str
    name: str
    organization: str  # 组织名
    description: str
    readme: str
    is_private: bool
    default_branch: str = "main"
    github_url: Optional[str]  # GitHub 集成
    local_path: str
    created_at: datetime
    updated_at: datetime
    owner_id: str
    collaborators: List[str]
```

### 2. Branch (分支) - 原 Task
```python
class Branch:
    id: str
    name: str  # feature/add-login, bugfix/xxx
    repository_id: str
    base_branch: str  # 基于哪个分支
    description: str  # 任务描述
    status: str  # draft, in_progress, review, merged, closed
    created_by: str
    assigned_to: Optional[str]
    pull_request_id: Optional[str]
    commits: List[Commit]
    created_at: datetime
    updated_at: datetime
```

### 3. Issue (议题) - 子任务
```python
class Issue:
    id: str
    number: int  # #123
    title: str
    description: str
    repository_id: str
    branch_id: Optional[str]  # 关联的分支
    status: str  # open, in_progress, resolved, closed
    labels: List[str]  # bug, feature, enhancement
    assigned_to: Optional[str]
    created_by: str
    comments: List[Comment]
    created_at: datetime
    updated_at: datetime
```

### 4. Commit (提交) - 任务执行记录
```python
class Commit:
    id: str
    branch_id: str
    message: str
    description: str
    author: str
    timestamp: datetime
    files_changed: List[str]
    additions: int
    deletions: int
    ai_generated: bool = True
```

## GitHub 集成功能

### 1. 仓库同步
```python
class GitHubIntegration:
    def sync_repository(self, repo_id: str):
        """同步本地仓库与 GitHub"""
        pass
    
    def import_from_github(self, github_url: str):
        """从 GitHub 导入仓库"""
        pass
    
    def create_github_branch(self, branch: Branch):
        """在 GitHub 创建对应分支"""
        pass
    
    def create_pull_request(self, branch: Branch):
        """创建 Pull Request"""
        pass
```

### 2. 工作流程

1. **创建仓库（项目）**
   ```bash
   # 本地创建
   claudetask repo create my-project
   
   # 从 GitHub 导入
   claudetask repo import https://github.com/user/repo
   ```

2. **创建分支（任务）**
   ```bash
   # 创建功能分支
   claudetask branch create feature/add-login
   
   # 创建修复分支
   claudetask branch create bugfix/fix-memory-leak
   ```

3. **创建议题（子任务）**
   ```bash
   # 在分支下创建议题
   claudetask issue create "设计登录界面" --branch feature/add-login
   ```

4. **执行任务（AI 生成代码）**
   ```bash
   # 执行分支任务
   claudetask execute feature/add-login
   
   # 执行特定议题
   claudetask execute issue-123
   ```

5. **提交和推送**
   ```bash
   # 查看更改
   claudetask status
   
   # 提交更改
   claudetask commit -m "feat: 实现用户登录功能"
   
   # 推送到 GitHub
   claudetask push
   
   # 创建 PR
   claudetask pr create
   ```

## API 端点设计

### Repository 管理
- `GET /api/repos` - 列出所有仓库
- `POST /api/repos` - 创建仓库
- `GET /api/repos/:id` - 获取仓库详情
- `PUT /api/repos/:id` - 更新仓库
- `DELETE /api/repos/:id` - 删除仓库
- `POST /api/repos/:id/sync` - 同步 GitHub

### Branch 管理
- `GET /api/repos/:repo_id/branches` - 列出分支
- `POST /api/repos/:repo_id/branches` - 创建分支
- `GET /api/branches/:id` - 获取分支详情
- `PUT /api/branches/:id` - 更新分支
- `DELETE /api/branches/:id` - 删除分支
- `POST /api/branches/:id/execute` - 执行任务

### Issue 管理
- `GET /api/repos/:repo_id/issues` - 列出议题
- `POST /api/repos/:repo_id/issues` - 创建议题
- `GET /api/issues/:id` - 获取议题详情
- `PUT /api/issues/:id` - 更新议题
- `POST /api/issues/:id/comments` - 添加评论

### Git 操作
- `POST /api/repos/:id/commit` - 提交更改
- `POST /api/repos/:id/push` - 推送到远程
- `POST /api/repos/:id/pull` - 拉取更新
- `POST /api/branches/:id/pr` - 创建 PR

## 前端 UI 设计

### 1. 仓库列表页面
- 卡片式展示仓库
- 显示分支数、议题数、最后更新时间
- 快速创建分支按钮
- GitHub 同步状态

### 2. 仓库详情页面
- 左侧：文件树
- 中间：README 或代码查看
- 右侧：分支列表、议题列表

### 3. 分支工作区
- 分支切换器
- 任务描述（README）
- 议题看板（开放、进行中、已完成）
- 提交历史
- AI 执行按钮

### 4. Git 操作面板
- 更改文件列表
- 提交消息输入
- Push/Pull 按钮
- PR 创建向导

## 实现优势

1. **直观的概念映射**：用户熟悉 GitHub 的工作流程
2. **版本控制集成**：天然支持代码版本管理
3. **协作友好**：支持多人协作开发
4. **可追溯性**：所有更改都有记录
5. **灵活的任务组织**：分支和议题的组合提供灵活性
6. **AI 增强**：在 Git 工作流中无缝集成 AI 代码生成

## 迁移计划

1. **第一阶段**：数据库结构调整
   - 添加新表：repositories, branches, issues, commits
   - 迁移现有 projects → repositories
   - 迁移现有 tasks → branches

2. **第二阶段**：API 开发
   - 实现仓库管理 API
   - 实现分支管理 API
   - 实现 Git 操作 API

3. **第三阶段**：GitHub 集成
   - 实现 GitHub API 调用
   - 实现同步机制
   - 实现 PR 创建

4. **第四阶段**：前端改造
   - 更新 UI 组件
   - 实现 Git 操作界面
   - 添加 GitHub 状态显示