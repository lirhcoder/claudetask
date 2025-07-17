# Claude Code Web - 后端服务

基于 Flask 的后端 API 服务，提供项目管理、文件操作和 Claude Code 任务执行功能。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 Claude CLI

运行自动检测脚本：
```bash
python setup_claude.py
```

或手动查找 Claude：
```bash
python find_claude.py  # Windows 专用
```

### 3. 配置环境

复制配置文件模板：
```bash
cp .env.example .env
# WSL 用户：
cp .env.wsl.example .env.wsl
```

编辑 `.env` 文件，设置必要的配置。

### 4. 启动服务

```bash
python run.py
```

或使用启动脚本：
```bash
# Linux/macOS/WSL:
./start.sh
```

服务将在 http://localhost:5000 启动。

## 📁 项目结构

```
backend/
├── routes/                 # API 路由
│   ├── api.py             # REST API 端点
│   └── websocket.py       # WebSocket 处理
├── services/              # 业务逻辑
│   ├── claude_executor.py # Claude 任务执行器
│   └── file_manager.py    # 文件管理服务
├── models/                # 数据模型
│   └── task.py           # 任务模型和数据库操作
├── utils/                 # 工具函数
│   ├── validators.py     # 输入验证
│   └── claude_detector.py # Claude 自动检测
├── app.py                 # Flask 应用工厂
├── config.py             # 配置管理
├── run.py                # 应用入口
├── setup_claude.py       # Claude 配置助手
├── find_claude.py        # Claude 查找工具
├── requirements.txt      # Python 依赖
├── .env.example          # 配置模板
└── .env.wsl.example      # WSL 配置模板
```

## 🔧 配置说明

### 环境变量

在 `.env` 文件中配置：

```bash
# Flask 配置
FLASK_ENV=development              # 运行环境: development/production
SECRET_KEY=your-secret-key         # 密钥（生产环境必须修改）

# 项目存储
PROJECTS_DIR=./projects            # 项目存储目录（相对或绝对路径）

# Claude CLI
CLAUDE_CODE_PATH=claude            # Claude 可执行文件路径

# 上传配置
UPLOAD_FOLDER=./uploads            # 上传文件临时目录
MAX_CONTENT_LENGTH=16777216        # 最大上传大小（字节）

# 任务配置
MAX_CONCURRENT_TASKS=5             # 最大并发任务数

# Socket.IO
SOCKETIO_ENABLED=true              # 是否启用 WebSocket

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 环境特定配置

系统按以下优先级加载配置文件：
1. `.env.wsl`（仅在 WSL 环境）
2. `.env`（默认配置）
3. `.env.local`（本地覆盖，不提交到版本控制）

### Claude CLI 配置

#### 自动检测
系统会自动在以下位置查找 Claude：
- 系统 PATH
- 常见安装目录
- npm/yarn 全局包

#### 手动配置
在 `.env` 中设置完整路径：
```bash
# Windows
CLAUDE_CODE_PATH=C:/Users/Username/AppData/Local/Programs/claude/claude.exe

# Linux/macOS
CLAUDE_CODE_PATH=/usr/local/bin/claude

# WSL 调用 Windows 版本
CLAUDE_CODE_PATH=/mnt/c/Users/Username/AppData/Local/Programs/claude/claude.exe
```

## 🚦 API 端点

### 项目管理

- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/:name` - 获取项目详情
- `PUT /api/projects/:name` - 更新项目（移动/重命名）
- `DELETE /api/projects/:name` - 删除项目

### 文件管理

- `POST /api/files/upload` - 上传文件
- `GET /api/files/:path` - 获取文件内容
- `PUT /api/files/:path` - 更新文件内容
- `DELETE /api/files/:path` - 删除文件

### 任务执行

- `POST /api/execute` - 执行 Claude 任务
- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/:id` - 获取任务详情
- `POST /api/tasks/:id/cancel` - 取消任务

### WebSocket 事件

连接地址：`ws://localhost:5000/socket.io/`

#### 客户端发送
- `execute_code` - 执行代码请求
- `subscribe_task` - 订阅任务更新
- `unsubscribe_task` - 取消订阅

#### 服务端发送
- `task_output` - 任务输出
- `task_complete` - 任务完成
- `task_error` - 任务错误
- `execution_started` - 任务开始
- `execution_error` - 执行错误

## 🔒 安全特性

1. **路径验证**
   - 防止路径遍历攻击
   - 限制访问系统目录

2. **文件类型限制**
   ```python
   ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', 
                        '.json', '.txt', '.md', '.html', '.css'}
   ```

3. **输入验证**
   - 项目名称：字母、数字、-、_
   - 文件路径：相对路径验证
   - 任务提示：长度限制（10000字符）

4. **CORS 配置**
   - 可配置允许的源
   - 默认仅允许本地开发端口

## 🐛 故障排除

### 常见问题

1. **Claude CLI 未找到**
   ```bash
   python setup_claude.py
   ```

2. **端口已被占用**
   修改 `run.py` 中的端口号：
   ```python
   app.run(host='0.0.0.0', port=5001)  # 改为其他端口
   ```

3. **数据库错误**
   删除损坏的数据库文件：
   ```bash
   rm tasks.db
   ```

4. **编码错误**
   系统自动处理多种编码，如仍有问题，检查文件编码。

### 日志查看

启用调试模式查看详细日志：
```bash
export FLASK_ENV=development
python run.py
```

## 🧪 测试

运行测试套件：
```bash
pytest
```

运行特定测试：
```bash
pytest tests/test_api.py
```

测试覆盖率：
```bash
pytest --cov=.
```

## 🔄 数据库迁移

数据库会自动创建和迁移。如需手动操作：

```python
from models.task import TaskDB
db = TaskDB()
# 数据库会自动初始化
```

清理旧数据（默认保留30天）：
```python
from models.task import TaskManager
manager = TaskManager()
manager.cleanup_old_tasks(days=30)
```

## 📝 开发指南

### 添加新的 API 端点

1. 在 `routes/api.py` 添加路由：
```python
@api_bp.route('/api/new-endpoint', methods=['GET'])
def new_endpoint():
    return jsonify({'message': 'Hello'})
```

2. 添加输入验证（`utils/validators.py`）
3. 添加业务逻辑（`services/`）
4. 更新文档

### 扩展文件类型支持

编辑 `config.py`：
```python
ALLOWED_EXTENSIONS = {'.py', '.js', '.new_extension'}
```

### 自定义任务执行器

继承 `ClaudeExecutor` 类：
```python
from services.claude_executor import ClaudeExecutor

class CustomExecutor(ClaudeExecutor):
    def _run_task(self, task):
        # 自定义执行逻辑
        pass
```

## 🤝 贡献

1. 遵循 PEP 8 代码规范
2. 添加适当的注释和文档
3. 编写单元测试
4. 提交前运行 `pytest`

## 📄 许可证

MIT License