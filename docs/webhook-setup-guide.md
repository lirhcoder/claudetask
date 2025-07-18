# GitHub Webhook 设置指南

GitHub Webhook 允许 ClaudeTask 实时接收 GitHub 仓库的事件通知，自动同步代码变更和议题状态。

## 功能特性

- **实时同步**：自动接收 push、pull request、issue 等事件
- **自动更新**：保持本地数据与 GitHub 同步
- **事件记录**：记录所有 webhook 事件供审计
- **安全验证**：支持 webhook 密钥验证

## 配置步骤

### 1. 设置环境变量

```bash
# 设置 webhook 密钥（可选但推荐）
export GITHUB_WEBHOOK_SECRET=your_webhook_secret

# 设置 GitHub 访问令牌（必需）
export GITHUB_ACCESS_TOKEN=your_github_token
```

### 2. 通过 API 创建 Webhook

```bash
# 为仓库创建 webhook
curl -X POST http://localhost:5000/api/repos/{repo_id}/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://your-domain.com/api/webhooks/github"
  }'
```

如果不指定 `webhook_url`，系统会使用默认的本地 URL。

### 3. 手动在 GitHub 创建 Webhook

也可以直接在 GitHub 仓库设置中创建：

1. 进入仓库设置 > Webhooks
2. 点击 "Add webhook"
3. 填写配置：
   - **Payload URL**: `https://your-domain.com/api/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: 与环境变量 `GITHUB_WEBHOOK_SECRET` 相同
   - **Events**: 选择需要的事件或 "Send me everything"

## 支持的事件

ClaudeTask 支持以下 GitHub 事件：

| 事件 | 说明 | 自动操作 |
|------|------|----------|
| `push` | 代码推送 | 更新仓库最后修改时间 |
| `pull_request` | PR 创建/更新/关闭 | 更新 PR 状态 |
| `issues` | 议题创建/更新/关闭 | 同步议题状态 |
| `issue_comment` | 议题评论 | 记录评论活动 |
| `create` | 创建分支/标签 | 同步新分支 |
| `delete` | 删除分支/标签 | 更新分支状态 |
| `release` | 发布版本 | 记录发布信息 |
| `star` | Star 仓库 | 更新 Star 统计 |
| `fork` | Fork 仓库 | 更新 Fork 统计 |

## API 端点

### Webhook 接收端点

```
POST /api/webhooks/github
```

GitHub 将事件发送到此端点。

### 测试端点

```
POST /api/webhooks/github/test
```

GitHub 发送 `ping` 事件测试连接。

### 查看事件历史

```
GET /api/webhooks/github/events?limit=50
```

返回最近的 webhook 事件记录。

### 管理 Webhook

```bash
# 创建 webhook
POST /api/repos/{repo_id}/webhook

# 删除 webhook
DELETE /api/repos/{repo_id}/webhook
```

## 本地测试

使用 ngrok 在本地测试 webhook：

```bash
# 安装 ngrok
brew install ngrok  # macOS
# 或从 https://ngrok.com 下载

# 暴露本地服务
ngrok http 5000

# 使用 ngrok 提供的 URL 作为 webhook URL
# 例如：https://abc123.ngrok.io/api/webhooks/github
```

## 安全建议

1. **始终使用 HTTPS**：确保 webhook URL 使用 HTTPS
2. **设置密钥**：配置 `GITHUB_WEBHOOK_SECRET` 验证请求来源
3. **限制 IP**：如果可能，限制只接受 GitHub IP 范围的请求
4. **监控日志**：定期检查 webhook 事件日志

## 故障排除

### Webhook 未触发

1. 检查 webhook URL 是否可访问
2. 查看 GitHub 仓库设置中的 webhook 交付历史
3. 确认事件类型已选中

### 签名验证失败

1. 确认 `GITHUB_WEBHOOK_SECRET` 与 GitHub 设置一致
2. 检查是否有额外的空格或换行

### 事件未处理

1. 查看服务器日志：`tail -f logs/app.log`
2. 检查事件类型是否被支持
3. 确认数据库连接正常

## 示例：完整设置流程

```bash
# 1. 设置环境变量
export GITHUB_WEBHOOK_SECRET=my_secret_key
export GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxx

# 2. 启动服务
cd backend
python run.py

# 3. 导入仓库
curl -X POST http://localhost:5000/api/repos/import \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/user/repo"}'

# 4. 创建 webhook（假设返回的 repo_id 是 "abc123"）
curl -X POST http://localhost:5000/api/repos/abc123/webhook

# 5. 验证 webhook
# 在 GitHub 仓库设置中点击 webhook 的 "Redeliver" 按钮

# 6. 查看事件
curl http://localhost:5000/api/webhooks/github/events
```

## 注意事项

- Webhook URL 必须是公网可访问的地址
- 本地开发时使用 ngrok 或类似工具
- 生产环境建议使用反向代理和 SSL 证书
- 定期清理旧的 webhook 事件记录