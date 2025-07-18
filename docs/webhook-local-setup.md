# 本地开发环境配置 GitHub Webhook

由于 GitHub 无法直接访问你的本地服务（localhost），需要使用隧道工具将本地端口暴露到公网。

## 方案 1：使用 ngrok（推荐）

### 1. 安装 ngrok

**Windows:**
1. 访问 https://ngrok.com/download
2. 下载 Windows 版本
3. 解压到任意目录（如 `C:\tools\ngrok`）
4. 添加到 PATH 环境变量（可选）

**或使用 Chocolatey:**
```powershell
choco install ngrok
```

### 2. 注册 ngrok 账号（免费）

1. 访问 https://ngrok.com/signup
2. 注册账号
3. 获取 authtoken

### 3. 配置 ngrok

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 4. 启动隧道

```bash
# 在新的命令行窗口中运行
ngrok http 5000
```

你会看到类似输出：
```
Session Status                online
Session Expires               1 hours, 59 minutes
Version                       3.5.0
Region                        Asia Pacific (ap)
Latency                       32ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5000
```

### 5. 配置 Webhook URL

使用 ngrok 提供的 HTTPS URL：
```
https://abc123.ngrok-free.app/api/webhooks/github
```

## 方案 2：使用 localtunnel

### 安装和使用

```bash
# 安装（需要 Node.js）
npm install -g localtunnel

# 启动隧道
lt --port 5000 --subdomain claudetask
```

Webhook URL：
```
https://claudetask.loca.lt/api/webhooks/github
```

## 方案 3：使用 Cloudflare Tunnel

### 1. 安装 cloudflared

**Windows:**
```powershell
# 下载最新版本
# https://github.com/cloudflare/cloudflared/releases

# 或使用 winget
winget install --id Cloudflare.cloudflared
```

### 2. 运行隧道

```bash
cloudflared tunnel --url http://localhost:5000
```

## 在 ClaudeTask 中配置 Webhook

### 方法 1：通过 Web 界面

1. 登录 ClaudeTask
2. 进入"设置"页面
3. 在 "GitHub 集成" 标签页
4. 设置以下配置：
   - **GitHub 访问令牌**: 你的 GitHub Personal Access Token
   - **Webhook 密钥**: 设置一个安全的密钥（如：`your-webhook-secret-123`）

### 方法 2：通过 API

```bash
# 为仓库创建 webhook
curl -X POST http://localhost:5000/api/repos/{repo_id}/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://abc123.ngrok-free.app/api/webhooks/github"
  }'
```

### 方法 3：在 GitHub 上手动创建

1. 进入 GitHub 仓库设置
2. 选择 "Webhooks" → "Add webhook"
3. 填写配置：
   - **Payload URL**: `https://你的隧道域名.ngrok-free.app/api/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: 与 ClaudeTask 中设置的 webhook 密钥相同
   - **Events**: 选择需要的事件或 "Send me everything"

## 环境变量配置

在启动后端服务前设置：

**Windows (CMD):**
```cmd
set GITHUB_WEBHOOK_SECRET=your-webhook-secret-123
python run.py
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_WEBHOOK_SECRET="your-webhook-secret-123"
python run.py
```

## 测试 Webhook

### 1. 使用 GitHub 的测试功能

在 GitHub Webhook 设置页面，点击 "Recent Deliveries" 中的任意一条，然后点击 "Redeliver" 重新发送。

### 2. 使用测试脚本

```bash
cd backend
python test_webhook.py https://你的隧道域名.ngrok-free.app
```

### 3. 查看 ngrok 请求日志

访问 http://localhost:4040 查看所有通过 ngrok 的请求。

## 注意事项

1. **免费版限制**：
   - ngrok 免费版会生成随机子域名
   - 每次重启需要更新 webhook URL
   - 有请求数量限制

2. **安全考虑**：
   - 始终使用 webhook secret 验证请求
   - 仅在开发环境使用隧道工具
   - 生产环境应部署到可公开访问的服务器

3. **调试技巧**：
   - 查看后端控制台日志
   - 使用 ngrok Web 界面查看请求详情
   - 检查 GitHub webhook 的 "Recent Deliveries"

## 常见问题

### Q: ngrok 连接超时
A: 
- 检查防火墙设置
- 尝试更换 region：`ngrok http 5000 --region us`

### Q: Webhook 返回 404
A: 
- 确认 URL 路径正确：`/api/webhooks/github`
- 检查后端路由是否正确注册

### Q: 签名验证失败
A: 
- 确保 GitHub 和 ClaudeTask 使用相同的 secret
- 检查是否有多余的空格或换行

## 生产环境部署建议

本地开发完成后，建议将应用部署到：
- 云服务器（AWS, Azure, GCP）
- PaaS 平台（Heroku, Railway, Render）
- 使用真实域名和 SSL 证书

这样就不需要隧道工具，webhook 会更稳定可靠。