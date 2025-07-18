# GitHub Webhook 本地开发替代方案

除了 ngrok，还有多种方案可以在本地开发时接收 GitHub Webhook。

## 1. 内网穿透工具

### LocalTunnel（开源免费）
```bash
# 安装（需要 Node.js）
npm install -g localtunnel

# 使用
lt --port 5000

# 指定子域名（可能需要多次尝试）
lt --port 5000 --subdomain claudetask
```
**优点**：完全免费，开源  
**缺点**：速度较慢，稳定性一般

### Cloudflare Tunnel（免费）
```bash
# Windows 下载
# https://github.com/cloudflare/cloudflared/releases

# 运行（无需注册）
cloudflared tunnel --url http://localhost:5000
```
**优点**：稳定，快速，无需注册  
**缺点**：URL 随机生成

### Bore（开源）
```bash
# 安装
cargo install bore-cli

# 使用
bore local 5000 --to bore.pub
```
**优点**：简单，开源  
**缺点**：需要 Rust 环境

### Serveo（免费）
```bash
# 无需安装，直接使用 SSH
ssh -R 80:localhost:5000 serveo.net

# 指定子域名
ssh -R claudetask:80:localhost:5000 serveo.net
```
**优点**：无需安装任何软件  
**缺点**：依赖 SSH，可能被防火墙阻止

### Pagekite（开源）
```bash
# Python 安装
pip install pagekite

# 使用（需要注册免费账号）
pagekite.py 5000 yourname.pagekite.me
```
**优点**：稳定，支持自定义域名  
**缺点**：需要注册

## 2. 开发专用方案

### VS Code Port Forwarding（如果使用 VS Code）
1. 在 VS Code 中打开项目
2. 打开终端，运行 Flask 应用
3. 点击端口标签页 → Forward Port → 5000
4. 选择 Public 可见性
5. 获得 https://...github.dev URL

**优点**：集成在 VS Code 中，方便  
**缺点**：仅限 VS Code 用户

### GitHub Codespaces（如果项目在 GitHub）
1. 在 GitHub 仓库中创建 Codespace
2. 在 Codespace 中运行应用
3. 端口会自动转发，获得公网 URL

**优点**：与 GitHub 深度集成  
**缺点**：有免费额度限制

## 3. 反向代理服务

### Telebit
```bash
# 安装
npm install -g telebit

# 使用
telebit http 5000
```

### Holepunch
```bash
# 安装
npm install -g holepunch

# 使用
holepunch 5000
```

## 4. 自建方案

### 使用云服务器做跳板
如果你有云服务器，可以设置 SSH 隧道：

```bash
# 在云服务器上开启 GatewayPorts
# /etc/ssh/sshd_config
GatewayPorts yes

# 从本地连接
ssh -R 8080:localhost:5000 user@your-server.com

# Webhook URL: http://your-server.com:8080/api/webhooks/github
```

### 使用 FRP（Fast Reverse Proxy）
1. 在云服务器上部署 frps（服务端）
2. 在本地运行 frpc（客户端）

**frpc.ini 配置：**
```ini
[common]
server_addr = your-server.com
server_port = 7000

[web]
type = http
local_port = 5000
custom_domains = webhook.your-domain.com
```

## 5. 开发替代方案

### 使用 Webhook 中继服务

#### Webhook.site
1. 访问 https://webhook.site
2. 获得一个临时 URL
3. 在 GitHub 设置这个 URL
4. 手动将收到的数据转发到本地

#### RequestBin
类似 webhook.site，可以查看和调试 webhook 请求

#### Hookdeck（专业 Webhook 管理）
```bash
# 安装 CLI
npm install -g hookdeck-cli

# 登录并转发
hookdeck login
hookdeck listen 5000
```

### 模拟 Webhook（推荐用于测试）

创建测试脚本直接向本地发送模拟的 GitHub webhook：

```python
# test_local_webhook.py
import requests
import json
import hmac
import hashlib

def send_test_webhook():
    # 模拟 GitHub push 事件
    payload = {
        "ref": "refs/heads/main",
        "repository": {
            "full_name": "test/repo",
            "html_url": "https://github.com/test/repo"
        },
        "pusher": {
            "name": "test-user"
        },
        "commits": [{
            "id": "abc123",
            "message": "Test commit",
            "author": {"name": "Test User"}
        }]
    }
    
    # 计算签名（如果配置了 secret）
    secret = "your-webhook-secret"
    signature = hmac.new(
        secret.encode('utf-8'),
        json.dumps(payload).encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # 发送请求
    response = requests.post(
        'http://localhost:5000/api/webhooks/github',
        json=payload,
        headers={
            'X-GitHub-Event': 'push',
            'X-Hub-Signature-256': f'sha256={signature}'
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == '__main__':
    send_test_webhook()
```

## 6. 最佳实践建议

### 开发阶段
1. **简单测试**：使用模拟脚本
2. **需要真实 GitHub 事件**：使用 Cloudflare Tunnel（最简单）
3. **长期开发**：LocalTunnel 或 Serveo

### 准生产阶段
1. **使用低成本云服务器**（如 Oracle Cloud 免费层）
2. **部署到 PaaS 平台**：
   - Heroku（有免费层）
   - Railway
   - Render
   - Fly.io

### 对比表

| 工具 | 免费 | 无需注册 | 稳定性 | 速度 | 固定URL |
|------|------|----------|--------|------|---------|
| ngrok | 限制 | ❌ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 付费 |
| Cloudflare Tunnel | ✅ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| LocalTunnel | ✅ | ✅ | ⭐⭐⭐ | ⭐⭐⭐ | 部分 |
| Serveo | ✅ | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 部分 |
| Webhook.site | ✅ | ✅ | ⭐⭐⭐⭐ | - | ❌ |
| VS Code | ✅ | ❌ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ |

## 7. 快速开始命令

```bash
# Cloudflare Tunnel（推荐）
cloudflared tunnel --url http://localhost:5000

# LocalTunnel
npx localtunnel --port 5000

# Serveo
ssh -R 80:localhost:5000 serveo.net

# 模拟测试
python test_local_webhook.py
```

选择适合你的方案，主要考虑：
- 是否需要安装软件
- 是否需要注册账号
- 稳定性要求
- 是否需要固定 URL