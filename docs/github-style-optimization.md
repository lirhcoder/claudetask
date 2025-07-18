# ClaudeTask GitHub 风格优化指南

## 优化概览

本次优化将 ClaudeTask 简化为更加直观的 GitHub 风格工作流，移除了冗余功能，统一了操作体验。

## 主要变更

### 1. 数据模型统一

**旧系统**：
- 项目 (Projects) → 任务 (Tasks) → 子任务 → 执行
- 多个并行的管理系统

**新系统**：
- 仓库 (Repositories) → 分支 (Branches/Tasks) → 提交 (Executions)
- 统一的 Git 工作流

### 2. API 简化

#### 统一 API V2
- `/api/v2/repos/{id}/quick-task` - 一键创建并执行任务
- `/api/v2/repos/{id}/branches` - 统一的分支/任务管理
- `/api/v2/dashboard` - 简化的仪表板数据

#### API 兼容性
旧 API 会自动转发到新 API，确保平滑过渡：
- `/api/projects` → `/api/repos`
- `/api/tasks` → `/api/branches`

### 3. UI 简化

#### 移除的页面
- 项目管理页面
- 独立的任务页面
- 任务工作台

#### 优化的页面
- **仓库详情页**：整合了任务创建和执行
- **工作台**：简化为核心统计和快捷操作
- **导航菜单**：从 7 个减少到 3 个主要入口

### 4. 核心功能增强

#### 快速任务按钮
```jsx
<QuickTaskButton repositoryId={repoId} />
```
- 一键创建任务分支
- 自动执行 AI 任务
- 可选自动提交和创建 PR

#### 简化的任务状态
- `draft` - 待执行
- `in_progress` - 执行中
- `completed` - 已完成
- `failed` - 失败

## 使用指南

### 1. 运行数据迁移

```bash
cd backend
python migrate_to_github.py
```

或使用批处理脚本：
```bash
run_migration.bat
```

### 2. 创建任务的新流程

1. 进入仓库页面
2. 点击"快速任务"按钮
3. 填写任务标题和提示词
4. 选择执行器（Claude/本地）
5. 点击"创建并执行"

系统会自动：
- 创建任务分支
- 执行 AI 任务
- 提交更改（如果启用）
- 创建 Pull Request（如果启用）

### 3. 配置简化

必要的配置项已简化为：
- GitHub 令牌
- GitHub Webhook 密钥
- Claude API 密钥
- 执行超时时间
- UI 主题和语言

## 技术细节

### 兼容性中间件

```python
class CompatibilityMiddleware:
    def __call__(self, environ, start_response):
        # 自动转发旧 API 到新 API
        path = environ.get('PATH_INFO', '')
        for old_path, new_path in self.api_mapping.items():
            if path.startswith(old_path):
                environ['PATH_INFO'] = new_path
                break
```

### 统一工作流类

```python
class UnifiedWorkflow:
    def create_and_execute(self, repo_id, task_data, user_id):
        # 1. 创建分支
        # 2. 配置执行
        # 3. 执行任务
        # 4. 处理结果
        # 5. 可选：创建 PR
```

## 最佳实践

1. **使用分支命名约定**：
   - 任务分支：`task/YYYYMMDDHHMM-description`
   - 功能分支：`feature/feature-name`

2. **利用自动化**：
   - 启用自动提交减少手动操作
   - 使用自动 PR 创建加快审核流程

3. **保持简单**：
   - 一个分支 = 一个任务
   - 使用描述性的任务标题
   - 充分利用 AI 执行器

## 后续计划

1. 添加 GitHub Actions 集成
2. 实现 PR 模板
3. 增强代码审查功能
4. 添加更多 AI 执行器选项

## 回滚指南

如果需要回滚到旧系统：

1. 恢复数据库备份：
   ```bash
   cp tasks.db.backup.YYYYMMDD_HHMMSS tasks.db
   ```

2. 删除迁移配置：
   ```bash
   rm migration_config.json
   ```

3. 重启服务

系统会自动恢复到原始状态。