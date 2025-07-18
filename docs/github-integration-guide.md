# GitHub 集成详细使用指南

## 目录

1. [前置准备](#前置准备)
2. [GitHub 配置](#github-配置)
3. [系统配置](#系统配置)
4. [创建和管理仓库](#创建和管理仓库)
5. [使用快速任务](#使用快速任务)
6. [Webhook 配置](#webhook-配置)
7. [常见问题](#常见问题)

## 前置准备

### 1. 创建 GitHub Personal Access Token

1. 登录 GitHub，进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 设置 Token 名称，例如："ClaudeTask Integration"
4. 选择权限范围（Scopes）：
   - ✅ `repo` - 完整的仓库控制
   - ✅ `workflow` - 更新 GitHub Actions 工作流
   - ✅ `admin:repo_hook` - 管理 webhooks
   - ✅ `read:user` - 读取用户信息
   - ✅ `read:org` - 读取组织信息（如果需要访问组织仓库）

5. 点击 "Generate token" 并复制生成的 token（只显示一次！）

### 2. 准备 Claude API Key

1. 访问 [Claude Console](https://console.anthropic.com/)
2. 创建或获取你的 API Key
3. 确保有足够的使用额度

## 系统配置

### 1. 在 ClaudeTask 中配置

1. 登录 ClaudeTask 系统
2. 进入"设置"页面
3. 切换到"GitHub 集成"标签
4. 填写配置：
   ```
   GitHub 访问令牌: ghp_xxxxxxxxxxxxxxxxxxxx
   GitHub Webhook 密钥: your-secure-webhook-secret-123
   ```
5. 点击"保存配置"

### 2. 配置 Claude API

1. 在"AI 执行器"标签中
2. 填写 Claude API Key
3. 设置执行超时时间（建议 300 秒）
4. 保存配置

## 创建和管理仓库

### 方式一：导入现有 GitHub 仓库

1. 进入"仓库"页面
2. 点击"导入 GitHub 仓库"
3. 输入仓库信息：
   ```
   组织/用户名: yourusername
   仓库名称: your-repo-name
   ```
4. 点击"导入"

系统会自动：
- 克隆仓库到本地
- 创建数据库记录
- 同步分支和 Issues

### 方式二：创建新仓库

1. 进入"仓库"页面
2. 点击"新建仓库"
3. 填写信息：
   ```
   仓库名称: my-new-project
   描述: 项目描述
   是否私有: ✅
   初始化 README: ✅
   ```
4. 点击"创建"

可选择：
- 仅创建本地仓库
- 同时在 GitHub 创建（需要配置 token）

## 使用快速任务

### 1. 创建并执行任务

1. 进入仓库详情页
2. 点击右上角"快速任务"按钮
3. 填写任务信息：

```yaml
任务标题: 修复登录页面的样式问题
执行提示词: |
  请修复 src/pages/login.jsx 中的样式问题：
  1. 登录按钮应该居中
  2. 输入框宽度应该一致
  3. 添加适当的间距
相关文件: src/pages/login.jsx, src/styles/login.css
执行器: Claude
自动提交: ✅
自动创建PR: ✅
```

4. 点击"创建并执行"

### 2. 任务执行流程

系统会自动：
1. 创建新分支：`task/20240118120000-fix-login-style`
2. 切换到新分支
3. 调用 Claude AI 执行任务
4. 自动提交更改（如果启用）
5. 创建 Pull Request（如果启用）
6. 更新 Agent 员工指数

### 3. 查看执行结果

执行完成后，你可以：
- 查看修改的文件列表
- 查看 AI 生成的提交信息
- 直接跳转到 GitHub PR 页面
- 查看执行日志

## Webhook 配置

### 1. 本地开发环境

使用 Cloudflare Tunnel（推荐）：

```bash
# 下载 cloudflared
# https://github.com/cloudflare/cloudflared/releases

# 运行隧道
cloudflared tunnel --url http://localhost:5000

# 获得类似这样的 URL：
# https://abc-def-ghi.trycloudflare.com
```

### 2. 在 GitHub 配置 Webhook

1. 进入 GitHub 仓库设置
2. 选择 Webhooks → Add webhook
3. 配置信息：
   ```
   Payload URL: https://your-domain.com/api/webhooks/github
   Content type: application/json
   Secret: your-secure-webhook-secret-123
   ```
4. 选择事件：
   - ✅ Pushes
   - ✅ Pull requests
   - ✅ Issues
   - ✅ Issue comments
   - ✅ Pull request reviews

5. 点击"Add webhook"

### 3. 验证 Webhook

1. GitHub 会发送 ping 事件
2. 在 Recent Deliveries 中查看状态
3. 应该看到 200 响应

## 工作流示例

### 示例 1：修复 Bug

```bash
# 1. 在 Issues 中创建问题
标题: 用户登录后跳转错误
描述: 用户登录成功后应该跳转到 dashboard，现在跳转到了首页

# 2. 在 ClaudeTask 中创建任务
任务标题: 修复登录后跳转错误 #123
提示词: 修复 Issue #123，登录成功后应该跳转到 /dashboard 而不是 /

# 3. 系统自动执行
- 创建分支：task/fix-login-redirect-123
- AI 分析并修复代码
- 提交：Fix login redirect issue #123
- 创建 PR 并关联 Issue

# 4. 代码审查
- 在 GitHub 上审查 PR
- 合并到主分支
- 自动关闭 Issue
```

### 示例 2：添加新功能

```bash
# 1. 创建功能分支
任务标题: 添加用户头像上传功能
提示词: |
  在用户设置页面添加头像上传功能：
  1. 添加文件上传组件
  2. 限制文件类型为图片
  3. 最大 5MB
  4. 显示上传预览
  5. 保存到 /api/user/avatar 端点

# 2. 分步执行
- 第一步：添加前端组件
- 第二步：实现后端 API
- 第三步：添加测试

# 3. 创建 PR
- 完整的功能描述
- 截图展示
- 测试说明
```

### 示例 3：代码重构

```bash
# 1. 创建重构任务
任务标题: 重构认证模块提取公共逻辑
提示词: |
  重构 auth 模块：
  1. 提取公共的验证逻辑到 utils/auth.js
  2. 统一错误处理
  3. 添加 JSDoc 注释
  4. 保持向后兼容

# 2. 执行重构
- AI 分析现有代码结构
- 提取公共函数
- 更新所有引用
- 确保测试通过
```

## 最佳实践

### 1. 分支命名规范

```
feature/add-user-avatar     # 新功能
fix/login-redirect-issue    # Bug 修复
refactor/auth-module       # 代码重构
task/20240118-description  # AI 任务
```

### 2. 提交信息规范

```
feat: 添加用户头像上传功能
fix: 修复登录后跳转错误
refactor: 重构认证模块
docs: 更新 API 文档
test: 添加用户头像上传测试
```

### 3. PR 描述模板

```markdown
## 概述
简要描述这个 PR 的目的

## 改动内容
- [ ] 添加了 XXX 功能
- [ ] 修复了 YYY 问题
- [ ] 重构了 ZZZ 模块

## 测试
- [ ] 单元测试通过
- [ ] 手动测试完成
- [ ] 无破坏性改动

## 截图（如适用）
[添加截图]

## 相关 Issue
Fixes #123
```

### 4. 安全建议

1. **Token 安全**
   - 不要在代码中硬编码 token
   - 使用环境变量或配置系统
   - 定期轮换 token

2. **Webhook 安全**
   - 使用强密钥
   - 验证 webhook 签名
   - 限制 IP（如果可能）

3. **权限控制**
   - 仅授予必要的权限
   - 使用细粒度的 token
   - 定期审查权限

## 常见问题

### Q: 同步失败提示 404

检查：
1. Token 是否有效
2. 仓库名称是否正确
3. 是否有仓库访问权限

### Q: Webhook 收不到事件

检查：
1. Webhook URL 是否正确
2. Secret 是否匹配
3. 选择了正确的事件类型
4. 查看 GitHub webhook 的 Recent Deliveries

### Q: AI 执行超时

解决方案：
1. 增加超时时间设置
2. 将大任务分解为小任务
3. 优化提示词，使其更具体

### Q: 分支冲突

处理方法：
1. 在创建任务前先同步仓库
2. 选择正确的基础分支
3. 手动解决冲突后再执行

### Q: PR 无法自动创建

检查：
1. Token 是否有 PR 权限
2. 分支是否有更改
3. 目标分支是否存在保护规则

## 进阶技巧

### 1. 批量任务处理

```python
# 创建多个相关任务
tasks = [
    "更新所有组件的 PropTypes",
    "添加组件的 TypeScript 定义",
    "更新组件文档"
]

for task in tasks:
    create_quick_task(task)
```

### 2. 使用 AI 进行代码审查

```yaml
任务标题: 审查 PR #456 的代码质量
提示词: |
  请审查 PR #456 的代码：
  1. 检查代码规范
  2. 发现潜在的 bug
  3. 提出优化建议
  4. 检查安全问题
```

### 3. 自动化工作流

结合 GitHub Actions：

```yaml
name: AI Task on Issue
on:
  issues:
    types: [opened, labeled]

jobs:
  create-task:
    if: contains(github.event.label.name, 'ai-task')
    runs-on: ubuntu-latest
    steps:
      - name: Trigger ClaudeTask
        run: |
          curl -X POST https://your-api/webhooks/github \
            -H "Content-Type: application/json" \
            -d '${{ toJson(github.event) }}'
```

## 获取帮助

- 查看日志：后端控制台和 `logs/` 目录
- GitHub Issues：提交问题和建议
- 文档更新：查看最新的文档更新

记住：AI 是辅助工具，最终代码质量需要人工把关！