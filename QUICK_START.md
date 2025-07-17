# 🚀 Claude Code Web 快速开始指南

本指南将帮助你在 5 分钟内启动 Claude Code Web。

## 📋 前置要求

- Python 3.9+ 和 pip
- Node.js 18+ 和 npm
- Git

## 🎯 快速安装（3步）

### 第 1 步：克隆并安装依赖

```bash
# 克隆项目
git clone <repository-url> claudetask
cd claudetask

# 安装后端依赖
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# 安装前端依赖（新开一个终端）
cd ../frontend
npm install
```

### 第 2 步：配置 Claude CLI

在后端目录运行自动配置：
```bash
cd backend
python setup_claude.py
```

按提示操作：
- 如果自动检测失败，选择 `y` 手动输入路径
- Windows 常见路径：`C:\Users\你的用户名\AppData\Roaming\npm\claude.cmd`

**没有安装 Claude？**
```bash
# Windows/Mac/Linux 通用方法：
npm install -g @anthropic/claude-cli
```

### 第 3 步：启动服务

**终端 1 - 启动后端：**
```bash
cd backend
python run.py
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

✅ **完成！** 打开浏览器访问 http://localhost:5173

## 🎮 基本使用

### 1. 创建第一个项目

1. 点击 "New Project"
2. 输入项目名称（如 "my-first-project"）
3. 点击 "Create"

### 2. 执行第一个任务

1. 打开刚创建的项目
2. 在右侧输入框输入：`创建一个简单的 Python Hello World 程序`
3. 点击 "Execute" 或按 Ctrl+Enter
4. 查看实时输出

### 3. 上传文件

1. 点击文件浏览器的上传按钮
2. 选择或拖拽文件
3. 文件会自动上传到当前项目

## 🔧 常见问题快速解决

### Claude CLI 未找到？

**Windows PowerShell:**
```powershell
# 查找 claude
where.exe claude
# 或
npm list -g @anthropic/claude-cli
```

**手动设置路径：**
编辑 `backend/.env`：
```
CLAUDE_CODE_PATH=C:/full/path/to/claude.cmd
```

### 端口被占用？

修改端口：
- 后端：编辑 `backend/run.py`，修改 `port=5000`
- 前端：编辑 `frontend/vite.config.js`，修改 `server.port`

### 任务一直是 Pending？

1. 检查 Claude CLI 是否正确安装
2. 查看后端控制台的错误信息
3. 确认项目路径存在

## 📝 下一步

- 查看完整 [README.md](README.md) 了解所有功能
- 阅读 [后端文档](backend/README.md) 了解 API
- 阅读 [前端文档](frontend/README.md) 了解 UI 组件
- 查看 [Claude 配置指南](backend/README_CLAUDE_SETUP.md)

## 💡 提示

1. **使用模板**：点击模板按钮使用预设提示语
2. **快捷键**：Ctrl+Enter 执行，Ctrl+S 保存文件
3. **批量上传**：支持拖拽多个文件
4. **实时输出**：任务执行时会实时显示进度

---

需要帮助？提交 [Issue](../../issues) 或查看 [故障排除](README.md#-故障排除)。