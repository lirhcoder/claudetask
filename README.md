# Claude Code Web

基于 Web 的 Claude Code 远程执行平台，提供直观的界面来管理项目和执行 AI 辅助编程任务。

## 🚀 功能特性

### 核心功能
- **项目管理** - 创建、浏览和管理多个项目
- **文件管理** - 文件树浏览、代码查看、文件上传
- **任务执行** - 通过 Web 界面调用 Claude Code
- **实时输出** - WebSocket 实时显示任务执行进度
- **任务历史** - 持久化存储所有执行记录
- **模板系统** - 预设和自定义任务模板

### 技术亮点
- 前后端分离架构
- SQLite 数据持久化
- WebSocket 双向通信
- 响应式 UI 设计
- Docker 容器化部署

## 📋 系统要求

- Python 3.9+
- Node.js 18+
- Claude Code CLI 已安装
- SQLite 3

## 🛠️ 快速开始

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd claudetask
```

2. **启动后端服务**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

3. **启动前端服务**
```bash
cd frontend
npm install
npm run dev
```

4. **访问应用**
```
http://localhost:5173
```

### Docker 部署

1. **构建并启动服务**
```bash
docker-compose up -d
```

2. **访问应用**
```
http://localhost:80
```

## 🏗️ 项目结构

```
claudetask/
├── backend/                 # Flask 后端
│   ├── app.py              # 应用入口
│   ├── routes/             # API 路由
│   │   ├── api.py          # REST API
│   │   └── websocket.py    # WebSocket 处理
│   ├── services/           # 业务逻辑
│   │   ├── claude_executor.py  # Claude 执行器
│   │   └── file_manager.py     # 文件管理
│   ├── models/             # 数据模型
│   │   └── task.py         # 任务模型和持久化
│   └── requirements.txt    # Python 依赖
│
├── frontend/               # React 前端
│   ├── src/
│   │   ├── components/     # UI 组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API 服务
│   │   └── stores/         # 状态管理
│   └── package.json        # Node 依赖
│
├── docker-compose.yml      # Docker 编排
└── README.md              # 本文档
```

## 💻 使用指南

### 创建项目
1. 点击 "New Project" 按钮
2. 输入项目名称（支持字母、数字、- 和 _）
3. 项目将在 `projects/` 目录下创建

### 执行任务
1. 打开项目页面
2. 在右侧输入框中输入提示语
3. 点击 "Execute" 或按 Ctrl+Enter
4. 实时查看执行输出

### 使用模板
1. 点击 "模板" 按钮
2. 选择预设模板或创建自定义模板
3. 模板中的 [占位符] 需要手动替换

### 上传文件
1. 在文件浏览器中点击上传按钮
2. 选择或拖拽文件
3. 支持批量上传，单文件限制 16MB

## 🔧 配置说明

### 环境变量
```bash
# 后端配置
CLAUDE_CODE_PATH=claude     # Claude 命令路径
MAX_CONCURRENT_TASKS=5      # 最大并发任务数
FLASK_ENV=development       # 运行环境

# 前端配置
REACT_APP_API_URL=http://localhost:5000  # API 地址
```

### 数据持久化
- 任务记录保存在 `tasks.db` SQLite 数据库
- 默认保留 30 天内的任务记录
- 模板数据保存在浏览器 localStorage

## 🚦 API 文档

### REST API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/projects` | GET | 获取项目列表 |
| `/api/projects` | POST | 创建新项目 |
| `/api/projects/:name` | GET | 获取项目详情 |
| `/api/execute` | POST | 执行 Claude 任务 |
| `/api/tasks` | GET | 获取任务列表 |
| `/api/tasks/:id` | GET | 获取任务详情 |
| `/api/tasks/:id/cancel` | POST | 取消任务 |
| `/api/files/upload` | POST | 上传文件 |
| `/api/files/:path` | GET | 获取文件内容 |

### WebSocket 事件

| 事件 | 方向 | 描述 |
|------|------|------|
| `execute_code` | Client→Server | 执行代码请求 |
| `task_output` | Server→Client | 任务输出行 |
| `task_complete` | Server→Client | 任务完成通知 |
| `subscribe_task` | Client→Server | 订阅任务更新 |

## 🔒 安全考虑

- 路径遍历防护
- 文件类型和大小限制
- 命令注入防护
- CORS 配置
- 生产环境建议添加身份认证

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发规范
- 后端使用 PEP 8 代码风格
- 前端使用 ESLint 配置
- 提交前运行测试

### 测试
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 📄 许可证

MIT License

## 🙏 致谢

- [Claude](https://claude.ai) - AI 编程助手
- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [React](https://reactjs.org/) - 前端框架
- [Ant Design](https://ant.design/) - UI 组件库
- [Socket.IO](https://socket.io/) - 实时通信库