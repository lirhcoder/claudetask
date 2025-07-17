# Windows 终端问题和解决方案

## Ctrl+Z SIGSTOP 错误

### 问题描述
在 Windows 终端中运行 Claude Code 时，如果按下 `Ctrl+Z`，会出现以下错误：
```
TypeError [ERR_UNKNOWN_SIGNAL]: Unknown signal: SIGSTOP
```

这是因为 Windows 不支持 UNIX 的 SIGSTOP 信号，但 Claude Code CLI 试图使用它来挂起进程。

### 解决方案

#### 方案1：使用包装脚本（推荐）
我们提供了两个包装脚本：

1. **claude_wrapper.bat** - 简单的批处理包装器
   - 提醒用户使用 Ctrl+C 而不是 Ctrl+Z
   - 显示友好的错误信息

2. **claude_safe_wrapper.ps1** - PowerShell 包装器
   - 尝试捕获并忽略 Ctrl+Z
   - 提供更好的错误处理

脚本会自动使用包装器（如果存在）。

#### 方案2：用户行为建议
- **使用 Ctrl+C** 来中断 Claude Code
- **避免使用 Ctrl+Z**
- 如果需要暂停，可以打开新的终端窗口

### 技术细节
- Windows 使用不同的进程控制机制
- SIGSTOP 是 UNIX/Linux 特有的信号
- Node.js 在 Windows 上不能处理 SIGSTOP

### 相关文件
- `/backend/claude_wrapper.bat` - Windows 批处理包装器
- `/backend/claude_safe_wrapper.ps1` - PowerShell 安全包装器
- `/backend/services/local_launcher.py` - 自动检测并使用包装器