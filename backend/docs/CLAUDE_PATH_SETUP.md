# Claude Path 配置指南

## 问题描述
执行本地任务时出现错误：`[WinError 2] 系统找不到指定的文件`

这是因为系统无法找到 `claude` 命令。

## 解决方案

### 方法1：自动检测（推荐）
运行检测脚本：
```bash
cd backend
python detect_claude.py
```

脚本会自动查找 Claude 并询问是否保存到配置文件。

### 方法2：手动配置环境变量
在 `backend/.env.local` 文件中添加：
```
CLAUDE_PATH=C:\Users\你的用户名\AppData\Roaming\npm\claude.cmd
```

### 方法3：添加到系统 PATH
1. 找到 claude 安装位置（通常在 `%APPDATA%\npm`）
2. 将该目录添加到系统 PATH 环境变量
3. 重启终端

## 常见 Claude 安装位置

### Windows
- `C:\Users\%USERNAME%\AppData\Roaming\npm\claude.cmd`
- `C:\Program Files\nodejs\claude.cmd`
- `C:\Program Files (x86)\nodejs\claude.cmd`

### macOS/Linux
- `/usr/local/bin/claude`
- `~/.npm-global/bin/claude`
- `/opt/homebrew/bin/claude`

## 验证安装
在命令行运行：
```bash
claude --version
```

如果显示版本信息，说明安装成功。

## 安装 Claude Code CLI
如果尚未安装：
```bash
npm install -g @anthropic-ai/claude-code
```

## 故障排除

### 1. npm 不在 PATH 中
先确保 Node.js 和 npm 已正确安装：
```bash
node --version
npm --version
```

### 2. 权限问题
使用管理员权限安装：
```bash
# Windows (管理员 PowerShell)
npm install -g @anthropic-ai/claude-code

# macOS/Linux
sudo npm install -g @anthropic-ai/claude-code
```

### 3. 使用 npx（无需全局安装）
如果不想全局安装，可以使用 npx：
```bash
npx @anthropic-ai/claude-code "你的提示词"
```

## 环境变量优先级
系统查找 Claude 的顺序：
1. `CLAUDE_PATH` 环境变量
2. 系统 PATH 中的 `claude`
3. 常见安装位置
4. 使用 `npx @anthropic-ai/claude-code`