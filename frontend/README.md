# Claude Code Web - 前端应用

基于 React + Vite + Ant Design 的现代化 Web 前端，提供直观的用户界面来管理项目和执行 Claude Code 任务。

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
# 或使用 yarn
yarn install
```

### 2. 配置环境（可选）

创建 `.env` 文件：
```bash
VITE_API_URL=http://localhost:5000
VITE_WS_URL=ws://localhost:5000
VITE_ENABLE_SOCKET=true
```

### 3. 启动开发服务器

```bash
npm run dev
# 或
yarn dev
```

应用将在 http://localhost:5173 启动。

### 4. 构建生产版本

```bash
npm run build
# 或
yarn build
```

构建产物在 `dist/` 目录。

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/         # 可复用组件
│   │   ├── CodeEditor.jsx # Monaco 代码编辑器
│   │   ├── FileExplorer.jsx # 文件树浏览器
│   │   ├── FileUpload.jsx # 文件上传组件
│   │   ├── TaskOutput.jsx # 任务输出显示
│   │   ├── TaskHistory.jsx # 任务历史列表
│   │   ├── TaskTemplates.jsx # 任务模板管理
│   │   └── ProjectManager.jsx # 项目卡片组件
│   ├── pages/             # 页面组件
│   │   ├── Dashboard.jsx  # 项目列表页
│   │   ├── ProjectPage.jsx # 项目详情页
│   │   └── LoginPage.jsx  # 登录页（预留）
│   ├── services/          # API 服务
│   │   └── api.js        # API 客户端
│   ├── stores/            # 状态管理
│   │   └── socketStore.js # WebSocket 状态
│   ├── styles/            # 样式文件
│   ├── App.jsx           # 根组件
│   ├── main.jsx          # 应用入口
│   └── router.jsx        # 路由配置
├── public/               # 静态资源
├── index.html           # HTML 模板
├── vite.config.js       # Vite 配置
├── package.json         # 项目配置
└── README.md           # 本文档
```

## 🎨 技术栈

- **React 18** - UI 框架
- **Vite** - 构建工具
- **Ant Design 5** - UI 组件库
- **React Router 6** - 路由管理
- **Axios** - HTTP 客户端
- **Socket.IO Client** - WebSocket 客户端
- **Monaco Editor** - 代码编辑器
- **Zustand** - 状态管理

## 🔧 功能模块

### 项目管理
- 项目列表展示
- 创建/删除项目
- 项目路径管理
- 项目卡片视图

### 文件管理
- 树形文件浏览器
- 文件上传（拖拽/选择）
- 文件编辑器
- 文件删除
- 编码自动检测

### 代码编辑器
- 语法高亮
- 多语言支持
- 主题切换
- 自动保存提醒
- 快捷键支持

### 任务执行
- 实时输出显示
- ANSI 颜色支持
- 任务状态跟踪
- 历史记录查看
- 模板系统

### UI/UX 特性
- 响应式设计
- 暗色模式支持
- 拖拽上传
- 键盘快捷键
- 加载状态反馈

## 🎯 核心组件

### CodeEditor
基于 Monaco Editor 的代码编辑器组件。

```jsx
<CodeEditor
  value={content}
  onChange={handleChange}
  language="javascript"
  readOnly={false}
  height="500px"
/>
```

### FileExplorer
递归渲染的文件树组件。

```jsx
<FileExplorer
  files={fileTree}
  onFileSelect={handleFileSelect}
  onFileDeleted={handleFileDeleted}
/>
```

### TaskOutput
支持 ANSI 转义序列的任务输出显示。

```jsx
<TaskOutput
  task={currentTask}
  height={400}
/>
```

### FileUpload
支持拖拽的文件上传组件。

```jsx
<FileUpload
  projectName={projectName}
  onUploadSuccess={handleSuccess}
  mode="dragger" // 或 "button"
/>
```

## 🔌 API 集成

### API 客户端配置

```javascript
// src/services/api.js
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
});
```

### 主要 API 方法

```javascript
// 项目管理
projectApi.listProjects()
projectApi.createProject(name)
projectApi.deleteProject(name)
projectApi.updateProject(name, newPath)

// 文件操作
projectApi.getFileContent(path)
projectApi.updateFileContent(path, content)
projectApi.deleteFile(path)
projectApi.uploadFile(formData)

// 任务执行
taskApi.executeTask(prompt, projectPath)
taskApi.listTasks()
taskApi.getTask(taskId)
```

### WebSocket 集成

```javascript
// 连接管理
const socket = io(wsUrl, {
  autoConnect: false,
  transports: ['websocket', 'polling']
});

// 事件监听
socket.on('task_output', (data) => {
  // 处理输出
});
```

## 🎨 样式定制

### Ant Design 主题

在 `App.jsx` 中配置：
```jsx
<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#1890ff',
    },
  }}
>
```

### 自定义样式

使用 CSS Modules：
```jsx
import styles from './Component.module.css'
```

## ⚡ 性能优化

1. **代码分割**
   - 路由级别的懒加载
   - 动态导入大型依赖

2. **状态管理**
   - 使用 Zustand 轻量级状态管理
   - 避免不必要的重渲染

3. **资源优化**
   - 图片懒加载
   - 虚拟滚动（长列表）

## 🧪 测试

运行测试：
```bash
npm test
```

运行测试覆盖率：
```bash
npm run test:coverage
```

## 🚀 部署

### 构建优化

```bash
npm run build
```

### 环境变量

生产环境配置：
```bash
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://api.example.com
```

### 静态服务器

使用任何静态文件服务器：
```bash
# 使用 serve
npx serve dist

# 使用 nginx
# 配置见 nginx.conf.example
```

## 🐛 故障排除

### 常见问题

1. **API 连接失败**
   - 检查后端服务是否运行
   - 确认 API URL 配置正确
   - 检查 CORS 设置

2. **WebSocket 连接问题**
   - 确认 WebSocket URL 正确
   - 检查防火墙设置
   - 尝试降级到轮询模式

3. **构建错误**
   - 清除 node_modules 和重装
   - 检查 Node.js 版本（需要 18+）

### 开发工具

- React Developer Tools
- Redux DevTools（如使用 Redux）
- Network 面板监控 API 请求

## 🤝 贡献指南

1. 遵循 ESLint 规则
2. 使用 Prettier 格式化代码
3. 组件使用 JSX 扩展名
4. 提交前运行 `npm run lint`

### 代码规范

- 使用函数组件和 Hooks
- Props 类型验证（PropTypes 或 TypeScript）
- 有意义的变量和函数命名
- 适当的注释和文档

## 📄 许可证

MIT License