# ClaudeTask 快速开始指南

本指南帮助你在 15 分钟内启动并运行 ClaudeTask。

## 🎯 目标

完成本指南后，你将能够：
- ✅ 运行 ClaudeTask 系统
- ✅ 创建第一个 AI 任务
- ✅ 集成 GitHub 仓库
- ✅ 查看员工指数

## 📦 第一步：下载和安装

### 1.1 获取代码

```bash
# 克隆仓库
git clone https://github.com/your-repo/claudetask.git
cd claudetask
```

### 1.2 安装后端依赖

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 1.3 安装前端依赖

```bash
# 新开一个终端
cd frontend
npm install
```

## ⚙️ 第二步：基础配置

### 2.1 创建环境变量文件

在 `backend` 目录创建 `.env` 文件：

```bash
cd backend
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

### 2.2 编辑 .env 文件

```env
# 必需配置
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Claude API（获取地址：https://console.anthropic.com/）
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx

# 可选：GitHub Token（获取地址：https://github.com/settings/tokens）
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
```

## 🚀 第三步：启动系统

### 3.1 启动后端服务

```bash
# 在 backend 目录，虚拟环境已激活
python run.py
```

你应该看到：
```
* Running on http://127.0.0.1:5000
* WebSocket support is enabled
```

### 3.2 启动前端服务

```bash
# 新终端，在 frontend 目录
npm run dev
```

你应该看到：
```
VITE v5.x.x ready in xxx ms
➜ Local: http://localhost:5173/
```

### 3.3 访问系统

打开浏览器访问：http://localhost:5173

## 👤 第四步：创建账号

### 4.1 默认管理员账号

首次运行时，系统自动创建管理员账号：
- 邮箱：`admin@claudetask.local`
- 密码：`admin123`

### 4.2 创建个人账号

1. 点击登录页面的"注册"
2. 填写邮箱和密码
3. 登录系统

## 🎉 第五步：创建第一个任务

### 5.1 创建本地仓库

1. 点击左侧菜单"仓库"
2. 点击"新建仓库"
3. 填写信息：
   ```
   仓库名称：my-first-project
   描述：我的第一个 AI 项目
   初始化 README：✅
   ```
4. 点击"创建"

### 5.2 执行 AI 任务

1. 进入刚创建的仓库
2. 点击右上角"快速任务"
3. 填写任务信息：
   ```
   任务标题：创建简单的待办事项应用
   执行提示词：创建一个简单的 HTML 待办事项应用，包含添加、删除和标记完成功能
   执行器：Claude
   自动提交：✅
   ```
4. 点击"创建并执行"

### 5.3 查看结果

- 实时查看 AI 执行过程
- 查看生成的文件
- 查看自动创建的 Git 提交

## 🔗 第六步：集成 GitHub（可选）

### 6.1 获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：`repo`, `workflow`
4. 生成并复制 token

### 6.2 配置 GitHub

1. 进入"设置"页面
2. 切换到"GitHub 集成"标签
3. 粘贴 GitHub Token
4. 保存配置

### 6.3 导入 GitHub 仓库

1. 返回"仓库"页面
2. 点击"导入 GitHub 仓库"
3. 输入：
   ```
   组织/用户名：your-username
   仓库名称：your-repo
   ```
4. 点击"导入"

## 📊 第七步：查看员工指数

1. 点击左侧菜单"员工指数"
2. 查看你的 AI 使用统计
3. 查看月度排行榜

## 🎯 下一步

恭喜！你已经成功运行 ClaudeTask。接下来可以：

1. **深入学习**
   - 阅读 [GitHub 集成指南](github-integration-guide.md)
   - 了解 [配置管理](configuration-guide.md)
   - 探索 [Agent 员工指数](agent-employee-index.md)

2. **高级功能**
   - 配置 Webhook
   - 创建任务模板
   - 批量任务处理

3. **团队协作**
   - 邀请团队成员
   - 设置权限
   - 查看团队统计

## ❓ 常见问题

### 端口被占用？

修改端口：
- 后端：编辑 `backend/config.py` 中的 `PORT`
- 前端：编辑 `frontend/vite.config.js` 中的 `server.port`

### Claude API 调用失败？

1. 检查 API Key 是否正确
2. 确认有足够的使用额度
3. 查看后端控制台错误信息

### 数据库错误？

删除 `backend/tasks.db` 文件，重启后端服务将自动重建。

### 前端页面空白？

1. 检查控制台错误
2. 清除浏览器缓存
3. 确保后端服务正在运行

## 🆘 获取帮助

- 查看完整文档：[文档目录](../README.md#📚-详细文档)
- 提交问题：[GitHub Issues](https://github.com/your-repo/claudetask/issues)
- 加入社区：[Discord Server](https://discord.gg/claudetask)

---

祝你使用愉快！🚀