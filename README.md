# ClaudeTask - AI 驱动的任务执行平台

基于 Web 的 AI 编程助手平台，集成 GitHub 工作流，提供智能任务执行、代码管理和团队协作功能。

## 🌟 核心特性

### GitHub 集成
- **仓库管理** - 导入和创建 GitHub 仓库，完整 Git 操作支持
- **快速任务** - 一键创建分支、执行 AI 任务、自动提交和创建 PR
- **Webhook 支持** - 自动同步 GitHub 事件（Issues、PR、Push 等）
- **分支工作流** - 基于 Git 分支的任务管理系统

### AI 执行能力
- **Claude 集成** - 使用 Claude AI 自动完成编程任务
- **智能提示优化** - 自动优化提示词，提高执行成功率
- **批量任务处理** - 支持任务链和批处理执行
- **实时输出** - WebSocket 实时显示执行进度

### 团队协作
- **Agent 员工指数** - 追踪团队成员 AI 使用效率
- **排行榜系统** - 月度和累计工作量排名
- **配置管理** - 集中管理团队配置和权限
- **多用户支持** - 完整的用户认证和授权体系

## 🚀 快速开始

### 1. 环境要求
- Python 3.9+
- Node.js 18+
- Git
- SQLite 3

### 2. 安装步骤

```bash
# 克隆项目
git clone https://github.com/your-repo/claudetask.git
cd claudetask

# 后端安装
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

# 前端安装
cd ../frontend
npm install
```

### 3. 配置系统

创建 `backend/.env` 文件：
```env
# Flask 配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Claude API
CLAUDE_API_KEY=your-claude-api-key

# GitHub 配置（可选）
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

### 4. 启动服务

```bash
# 启动后端（新终端）
cd backend
python run.py

# 启动前端（新终端）
cd frontend
npm run dev
```

访问 http://localhost:5173

## 📚 详细文档

- [GitHub 集成指南](docs/github-integration-guide.md) - 完整的 GitHub 功能使用说明
- [配置管理指南](docs/configuration-guide.md) - 系统配置详解
- [Agent 员工指数](docs/agent-employee-index.md) - 团队效率追踪系统
- [Webhook 配置](docs/webhook-local-setup.md) - 本地开发 Webhook 设置
- [API 文档](docs/api-reference.md) - RESTful API 参考

## 🔥 主要功能

### 1. 仓库管理
- 导入现有 GitHub 仓库
- 创建新仓库（本地或 GitHub）
- 同步仓库状态和分支
- 管理 Issues 和 Pull Requests

### 2. 快速任务执行
```yaml
任务示例：
- 标题：修复登录页面样式
- 提示：调整按钮居中，统一输入框宽度
- 自动功能：创建分支 → AI 执行 → 提交代码 → 创建 PR
```

### 3. 配置中心
- GitHub Token 管理
- Claude API 配置
- Webhook 密钥设置
- 执行参数调整

### 4. 员工指数系统
- 实时追踪 AI 任务执行时间
- 计算月度和累计员工指数
- 团队排行榜和历史趋势
- 管理员统计面板

## 🏗️ 系统架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端界面   │────▶│   后端API   │────▶│   数据库    │
│   (React)   │     │   (Flask)   │     │  (SQLite)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              ┌─────────┐   ┌─────────┐
              │ Claude  │   │ GitHub  │
              │   API   │   │   API   │
              └─────────┘   └─────────┘
```

## 🛡️ 安全特性

- 用户认证和会话管理
- API Token 加密存储
- Webhook 签名验证
- 权限分级控制
- 审计日志记录

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 提交规范
- `feat:` 新功能
- `fix:` 错误修复
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Claude](https://www.anthropic.com/claude) - AI 编程助手
- [GitHub API](https://docs.github.com/en/rest) - 代码托管平台
- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [React](https://reactjs.org/) - 前端框架
- [Ant Design](https://ant.design/) - UI 组件库

## 📞 联系支持

- 提交 Issue：[GitHub Issues](https://github.com/your-repo/claudetask/issues)
- 邮件联系：support@claudetask.com
- 文档网站：https://docs.claudetask.com

---

Made with ❤️ by ClaudeTask Team