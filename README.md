# Claude Code Web

基于 Web 的 Claude Code 远程执行平台，提供直观的界面来管理项目和执行 AI 辅助编程任务。

## 🌟 最新功能

- **任务链系统** - 创建父子任务，实现连续执行和上下文传递
- **提示词优化器** - 自动优化提示词，避免交互中断
- **项目路径管理** - 支持显示、修改项目绝对路径
- **项目删除功能** - 安全删除项目及其所有内容
- **文件编辑器** - 内置代码编辑器，支持语法高亮
- **多编码支持** - 自动检测文件编码（UTF-8、GBK、GB2312等）
- **Claude 自动检测** - 智能检测 Claude CLI 安装位置
- **跨平台支持** - 支持 Windows、Linux、WSL、macOS

## 🚀 功能特性

### 核心功能
- **项目管理** - 创建、浏览、修改路径、删除项目
- **文件管理** - 文件树浏览、代码查看/编辑、文件上传/下载/删除
- **任务执行** - 通过 Web 界面调用 Claude Code
- **任务链** - 创建父子任务序列，自动传递上下文
- **实时输出** - WebSocket 实时显示任务执行进度
- **任务历史** - 持久化存储所有执行记录
- **模板系统** - 预设和自定义任务模板
- **提示优化** - 智能检测并优化提示词，避免交互中断

### 技术亮点
- 前后端分离架构
- SQLite 数据持久化
- WebSocket 双向通信
- 响应式 UI 设计
- 自动路径转换（Windows/WSL）
- 环境自适应配置

## 📋 系统要求

- Python 3.9+
- Node.js 18+
- Claude Code CLI（系统会自动检测）
- SQLite 3

## 🛠️ 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd claudetask
```

### 2. 安装 Claude CLI

#### Windows
```powershell
# 通过 npm 安装（推荐）
npm install -g @anthropic/claude-cli

# 或从 GitHub 下载
# https://github.com/anthropics/claude-cli/releases
```

#### Linux/macOS/WSL
```bash
# 官方安装脚本
curl -fsSL https://claude.ai/install.sh | sh

# 或通过 npm
npm install -g @anthropic/claude-cli
```

### 3. 配置后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS/WSL:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行 Claude 检测脚本
python setup_claude.py

# 启动后端服务
python run.py
```

### 4. 配置前端

```bash
cd frontend
npm install
npm run dev
```

### 5. 访问应用
打开浏览器访问 http://localhost:5173

## 🔧 配置说明

### Claude CLI 配置

系统支持多种配置方式：

1. **自动检测**（推荐）
   ```bash
   python backend/setup_claude.py
   ```

2. **手动配置**
   在 `backend/.env` 文件中设置：
   ```bash
   CLAUDE_CODE_PATH=C:/path/to/claude.exe  # Windows
   CLAUDE_CODE_PATH=/usr/local/bin/claude  # Linux/macOS
   ```

3. **环境特定配置**
   - WSL 环境自动加载 `.env.wsl`
   - 本地覆盖使用 `.env.local`

### 环境变量

创建 `backend/.env` 文件：

```bash
# Flask 配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# 项目目录（默认为 ./projects）
PROJECTS_DIR=./projects

# Claude CLI 路径（自动检测或手动设置）
CLAUDE_CODE_PATH=claude

# 上传配置
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# 并发任务数
MAX_CONCURRENT_TASKS=5
```

### 前端配置

在 `frontend/.env` 中配置（可选）：
```bash
VITE_API_URL=http://localhost:5000
VITE_WS_URL=ws://localhost:5000
```

## 💻 使用指南

### 项目管理

1. **创建项目**
   - 点击 "New Project"
   - 输入项目名称
   - 可选择初始化 README

2. **修改项目路径**
   - 在项目页面点击路径旁的编辑按钮
   - 输入新路径（支持绝对路径或相对路径）
   - 系统会自动移动项目到新位置

3. **删除项目**
   - 在项目列表点击删除按钮
   - 确认后永久删除项目及所有文件

### 文件操作

1. **文件编辑**
   - 点击文件查看内容
   - 点击编辑按钮进入编辑模式
   - 支持语法高亮和自动保存提醒

2. **文件上传**
   - 点击上传按钮或拖拽文件
   - 支持批量上传
   - 自动处理文件编码

3. **文件删除**
   - 右键文件选择删除
   - 支持批量选择

### 执行任务

1. **基本执行**
   ```
   输入提示语 → 点击 Execute 或按 Ctrl+Enter
   ```

2. **使用模板**
   - 点击模板按钮选择预设模板
   - 替换 [占位符] 为实际内容
   - 自定义模板保存在本地

3. **任务链执行**
   - 点击"创建任务链"按钮
   - 添加多个相关任务（父任务 + 子任务）
   - 子任务会自动继承父任务的上下文
   - 支持使用预设的任务链模板

4. **提示词优化**
   - 点击"优化"按钮自动改进提示词
   - 添加非交互指令，避免执行中断
   - 智能检测可能的交互场景

5. **查看历史**
   - 点击历史按钮查看所有任务
   - 支持按状态筛选
   - 可以查看详细输出

## 🏗️ 项目结构

```
claudetask/
├── backend/                    # Flask 后端
│   ├── routes/                # API 路由
│   │   ├── api.py            # REST API 端点
│   │   └── websocket.py      # WebSocket 处理
│   ├── services/             # 业务逻辑
│   │   ├── claude_executor.py # Claude 执行器
│   │   └── file_manager.py   # 文件管理
│   ├── models/               # 数据模型
│   │   └── task.py          # 任务模型
│   ├── utils/                # 工具函数
│   │   ├── validators.py    # 输入验证
│   │   └── claude_detector.py # Claude 检测
│   ├── setup_claude.py       # Claude 配置助手
│   ├── .env.example          # 配置示例
│   └── requirements.txt      # Python 依赖
│
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/      # UI 组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API 服务
│   │   └── stores/         # 状态管理
│   └── package.json        # Node 依赖
│
└── README.md               # 本文档
```

## 🚦 API 文档

### REST API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/projects` | GET | 获取项目列表 |
| `/api/projects` | POST | 创建新项目 |
| `/api/projects/:name` | GET | 获取项目详情 |
| `/api/projects/:name` | PUT | 更新项目（移动/重命名） |
| `/api/projects/:name` | DELETE | 删除项目 |
| `/api/execute` | POST | 执行 Claude 任务 |
| `/api/tasks` | GET | 获取任务列表 |
| `/api/tasks/:id` | GET | 获取任务详情 |
| `/api/tasks/:id/cancel` | POST | 取消任务 |
| `/api/files/upload` | POST | 上传文件 |
| `/api/files/:path` | GET | 获取文件内容 |
| `/api/files/:path` | PUT | 更新文件内容 |
| `/api/files/:path` | DELETE | 删除文件 |

### WebSocket 事件

| 事件 | 方向 | 描述 |
|------|------|------|
| `execute_code` | Client→Server | 执行代码请求 |
| `task_output` | Server→Client | 任务输出行 |
| `task_complete` | Server→Client | 任务完成通知 |
| `task_error` | Server→Client | 任务错误通知 |
| `subscribe_task` | Client→Server | 订阅任务更新 |
| `unsubscribe_task` | Client→Server | 取消订阅 |

## 🔒 安全特性

- **路径验证** - 防止路径遍历攻击
- **文件类型限制** - 仅允许安全的文件类型
- **大小限制** - 上传文件大小限制（默认 16MB）
- **输入验证** - 所有用户输入都经过验证
- **CORS 配置** - 可配置的跨域策略

## 🐛 故障排除

### Claude CLI 未找到

1. 运行检测脚本：
   ```bash
   python backend/setup_claude.py
   ```

2. 查找 Claude 位置：
   ```bash
   python backend/find_claude.py
   ```

3. 手动设置路径：
   编辑 `backend/.env`：
   ```bash
   CLAUDE_CODE_PATH=/full/path/to/claude
   ```

### 文件编码错误

系统自动尝试多种编码（UTF-8、GBK、GB2312、Latin-1）。如果仍有问题，请确保文件使用标准编码。

### 任务执行失败

1. 检查 Claude CLI 是否正确安装
2. 确认项目路径存在且有权限
3. 查看后端日志获取详细错误信息

### Windows/WSL 路径问题

系统自动处理路径转换：
- Windows: `C:\path\to\project`
- WSL: `/mnt/c/path/to/project`

## 🤝 贡献指南

欢迎贡献代码！请遵循以下规范：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- **Python**: 遵循 PEP 8
- **JavaScript**: 使用 ESLint 配置
- **提交信息**: 使用语义化提交规范

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

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Claude](https://claude.ai) - AI 编程助手
- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [React](https://reactjs.org/) - 前端框架
- [Ant Design](https://ant.design/) - UI 组件库
- [Socket.IO](https://socket.io/) - 实时通信库
- [Monaco Editor](https://microsoft.github.io/monaco-editor/) - 代码编辑器

---

如有问题或建议，请提交 [Issue](../../issues) 或联系维护者。