# Claude CLI 配置指南

## 自动检测功能

系统现在支持自动检测 Claude CLI 的安装路径。

### 运行检测脚本

```bash
cd backend
python setup_claude.py
```

这个脚本会：
1. 检测当前运行环境（Windows/Linux/WSL/macOS）
2. 自动查找 Claude CLI 的安装位置
3. 测试 Claude CLI 是否可以正常执行
4. 提供配置建议
5. 可选：自动创建配置文件

## 环境特定配置

系统会根据环境自动加载不同的配置文件：

- **WSL 环境**: 优先加载 `.env.wsl`
- **其他环境**: 加载 `.env`
- **本地覆盖**: `.env.local`（始终最后加载）

### WSL 环境

在 WSL 中，系统会检查 `/proc/version` 文件来识别 WSL 环境，并自动加载 `.env.wsl`。

常见的 Claude 安装路径：
- `/usr/local/bin/claude`
- `~/.local/bin/claude`
- `~/bin/claude`
- `/snap/bin/claude`

### Windows 环境

在 Windows 中，系统会检查：
- `%APPDATA%\Local\Programs\claude\claude.exe`
- `C:\Program Files\claude\claude.exe`
- `%USERPROFILE%\.claude\bin\claude.exe`

## 手动配置

如果自动检测失败，可以手动设置：

1. 复制配置文件模板：
   ```bash
   cp .env.example .env
   # 或者对于 WSL
   cp .env.wsl.example .env.wsl
   ```

2. 编辑配置文件，设置 Claude 路径：
   ```
   CLAUDE_CODE_PATH=/path/to/claude
   ```

## 优先级

Claude 路径的查找优先级：
1. 环境变量 `CLAUDE_CODE_PATH`
2. 自动检测的路径
3. 默认值 `claude`（假设在 PATH 中）

## 故障排除

### Claude 未找到

如果系统提示找不到 Claude，请：

1. 确认 Claude CLI 已安装
2. 运行 `setup_claude.py` 查看检测结果
3. 手动设置 `CLAUDE_CODE_PATH` 环境变量

### 权限问题

在 Linux/WSL 中，确保 Claude 有执行权限：
```bash
chmod +x /path/to/claude
```

### WSL 调用 Windows 版本

如果想在 WSL 中使用 Windows 版本的 Claude：
```
CLAUDE_CODE_PATH=/mnt/c/Users/YourName/AppData/Local/Programs/claude/claude.exe
```