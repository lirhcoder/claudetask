# 配置管理指南

ClaudeTask 现在支持通过 Web 界面管理所有系统配置，无需手动编辑配置文件或设置环境变量。

## 访问设置页面

1. 登录 ClaudeTask
2. 点击左侧菜单的"设置"图标
3. 进入系统设置页面

## 配置分类

### 1. GitHub 集成

配置 GitHub 相关功能：

- **GitHub 访问令牌** (`github.access_token`)
  - 用于访问 GitHub API
  - 获取方式：GitHub Settings → Developer settings → Personal access tokens
  - 权限要求：repo, workflow

- **Webhook 密钥** (`github.webhook_secret`)
  - 用于验证 GitHub Webhook 请求
  - 建议使用强密码

- **默认分支** (`github.default_branch`)
  - 新仓库的默认分支名称
  - 默认值：main

- **自动同步** (`github.auto_sync`)
  - 是否自动同步仓库信息
  - 默认值：关闭

### 2. Claude API

配置 AI 功能：

- **API 密钥** (`claude.api_key`)
  - Claude API 访问密钥
  - 从 Anthropic 控制台获取

- **模型选择** (`claude.model`)
  - 可选：claude-3-opus, claude-3-sonnet, claude-3-haiku
  - 默认：claude-3-opus

- **温度参数** (`claude.temperature`)
  - 控制输出随机性（0-1）
  - 默认值：0.7

- **最大令牌数** (`claude.max_tokens`)
  - 单次响应最大长度
  - 默认值：4096

### 3. 任务执行

控制任务执行行为：

- **默认超时时间** (`task.default_timeout`)
  - 任务执行超时（秒）
  - 默认值：600（10分钟）

- **最大重试次数** (`task.max_retries`)
  - 任务失败后的重试次数
  - 默认值：3

- **自动保存** (`task.auto_save`)
  - 自动保存任务结果
  - 默认值：启用

- **日志级别** (`task.log_level`)
  - 可选：DEBUG, INFO, WARNING, ERROR
  - 默认值：INFO

### 4. 界面设置

自定义用户界面：

- **自动刷新** (`ui.auto_refresh`)
  - 启用页面自动刷新
  - 默认值：关闭

- **刷新间隔** (`ui.refresh_interval`)
  - 自动刷新间隔（秒）
  - 默认值：5

- **界面主题** (`ui.theme`)
  - 可选：light, dark
  - 默认值：light

- **界面语言** (`ui.language`)
  - 可选：zh-CN, en-US
  - 默认值：zh-CN

### 5. 系统设置

高级系统配置（需要管理员权限）：

- **调试模式** (`system.debug_mode`)
  - 启用详细日志输出
  - 默认值：关闭

- **会话超时** (`system.session_timeout`)
  - 用户会话超时时间（秒）
  - 默认值：86400（24小时）

- **最大上传大小** (`system.max_upload_size`)
  - 文件上传大小限制（字节）
  - 默认值：10MB

## 使用说明

### 保存配置

1. 修改需要的配置项
2. 点击"保存更改"按钮
3. 系统会自动应用新配置

### 重置配置

如需恢复默认设置：
1. 点击"重置为默认"按钮
2. 确认操作
3. 所有配置将恢复到初始值

### 配置生效

- 大部分配置立即生效
- 某些系统级配置需要重启服务：
  - 调试模式
  - 会话超时
  - Claude 模型

### 安全提示

- 敏感信息（如 API 密钥）会被加密存储
- 在界面上显示时会被部分隐藏
- 建议定期更新密钥和令牌

## 从环境变量迁移

如果之前使用环境变量配置，可以运行迁移脚本：

```bash
cd backend
python3 migrate_env_to_config.py
```

支持的环境变量映射：
- `GITHUB_ACCESS_TOKEN` → `github.access_token`
- `GITHUB_WEBHOOK_SECRET` → `github.webhook_secret`
- `CLAUDE_API_KEY` → `claude.api_key`
- `CLAUDE_MODEL` → `claude.model`
- `DEBUG` → `system.debug_mode`
- `SESSION_TIMEOUT` → `system.session_timeout`

## API 访问

配置也可以通过 API 管理：

```javascript
// 获取所有配置
GET /api/configs

// 获取特定分类
GET /api/configs?category=github

// 更新配置
PUT /api/configs
{
  "configs": {
    "github.access_token": "your_token",
    "claude.temperature": 0.8
  }
}

// 重置为默认
POST /api/configs/reset
```

## 故障排除

### 配置不生效

1. 检查是否保存成功
2. 查看是否需要重启服务
3. 确认用户权限（系统配置需要管理员）

### 无法保存配置

1. 检查网络连接
2. 确认登录状态
3. 查看浏览器控制台错误

### 配置丢失

1. 配置存储在数据库中
2. 检查 `tasks.db` 文件是否存在
3. 可以使用重置功能恢复默认值