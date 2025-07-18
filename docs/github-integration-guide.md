# GitHub 集成使用指南

ClaudeTask 现已支持与 GitHub 深度集成，将项目作为仓库管理，任务作为分支，子任务作为议题，实现完整的代码开发工作流。

## 功能概览

- **仓库管理**：创建本地仓库或导入 GitHub 仓库
- **分支管理**：创建分支并使用 AI 执行任务
- **议题管理**：创建和跟踪子任务
- **Git 操作**：提交、推送、拉取代码
- **Pull Request**：创建 PR 进行代码审查

## 快速开始

### 1. 配置 GitHub 访问令牌（可选）

如果需要访问私有仓库或执行写操作，需要设置 GitHub 访问令牌：

```bash
export GITHUB_ACCESS_TOKEN=your_github_personal_access_token
```

获取令牌：访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)

### 2. 导入 GitHub 仓库

1. 进入"仓库管理"页面
2. 点击"导入 GitHub 仓库"按钮
3. 输入仓库地址，如：`https://github.com/username/repository`
4. 点击"开始导入"

系统会自动：
- 克隆仓库到本地
- 同步分支和议题信息
- 创建本地仓库记录

### 3. 创建分支执行任务

1. 进入仓库详情页
2. 在"分支"标签页点击"新建分支"
3. 填写分支名称和任务描述
4. 点击分支的"执行"按钮，AI 将自动完成编码任务

### 4. 创建议题跟踪子任务

1. 在仓库详情页切换到"议题"标签
2. 点击"新建议题"
3. 填写议题标题和描述
4. 可选择关联到特定分支

### 5. 提交和推送代码

完成开发后，可以通过 API 进行 Git 操作：

- **提交代码**：`POST /api/repos/{repo_id}/commit`
- **推送到远程**：`POST /api/repos/{repo_id}/push`
- **拉取更新**：`POST /api/repos/{repo_id}/pull`

### 6. 创建 Pull Request

分支开发完成后，可以创建 PR：

- **创建 PR**：`POST /api/branches/{branch_id}/pr`

## 工作流示例

### 示例 1：修复 Bug

1. 导入项目仓库
2. 创建分支 `fix/login-error`，描述："修复登录页面报错问题"
3. AI 自动分析并修复问题
4. 创建 PR 进行代码审查
5. 合并到主分支

### 示例 2：新功能开发

1. 创建分支 `feature/user-profile`
2. 创建多个议题：
   - "设计用户资料数据模型"
   - "实现用户资料 API"
   - "创建用户资料页面"
3. AI 逐步完成各个议题
4. 提交代码并创建 PR

## API 参考

### 仓库管理

```javascript
// 导入仓库
POST /api/repos/import
{
  "github_url": "https://github.com/username/repository"
}

// 同步仓库
POST /api/repos/{repo_id}/sync

// 创建仓库
POST /api/repos
{
  "name": "my-project",
  "description": "项目描述",
  "organization": "personal",
  "is_private": false,
  "github_url": "https://github.com/username/repository"
}
```

### 分支管理

```javascript
// 创建分支
POST /api/repos/{repo_id}/branches
{
  "name": "feature/new-feature",
  "base_branch": "main",
  "description": "实现新功能"
}

// 执行分支任务
POST /api/branches/{branch_id}/execute
```

### Git 操作

```javascript
// 提交代码
POST /api/repos/{repo_id}/commit
{
  "message": "fix: 修复登录错误",
  "branch": "fix/login-error"
}

// 推送到远程
POST /api/repos/{repo_id}/push
{
  "branch": "fix/login-error"
}

// 创建 Pull Request
POST /api/branches/{branch_id}/pr
{
  "title": "修复登录错误",
  "description": "修复了用户无法登录的问题",
  "base_branch": "main"
}
```

## 注意事项

1. **访问权限**：未设置 TOKEN 时只能访问公开仓库
2. **API 限制**：未认证用户每小时 60 次请求，认证用户 5000 次
3. **本地 Git**：确保系统已安装 Git 命令行工具
4. **仓库路径**：仓库克隆到 `repositories/{user_id}/{repo_name}/`

## 故障排除

### 导入仓库失败

- 检查仓库 URL 格式是否正确
- 确认仓库是否存在且可访问
- 私有仓库需要设置访问令牌

### Git 操作失败

- 确保已安装 Git：`git --version`
- 检查是否有未提交的更改
- 确认分支是否存在

### API 速率限制

- 设置 GitHub 访问令牌提高限制
- 避免频繁调用 API
- 使用同步功能批量更新数据

## 高级功能（规划中）

- [ ] GitHub Webhook 自动同步
- [ ] PR 自动合并
- [ ] Issue 自动分配
- [ ] CI/CD 集成
- [ ] 代码审查建议

## 更多帮助

如有问题，请查看：
- [GitHub API 文档](https://docs.github.com/en/rest)
- [Git 使用指南](https://git-scm.com/doc)
- ClaudeTask 项目 Issues