# ClaudeTask 后端启动说明

## 问题诊断

您遇到的 500 错误可能由以下原因导致：

1. **Flask 未在虚拟环境中安装**
2. **数据库表结构问题**（已通过代码修复）
3. **后端服务未正确启动**

## 解决方案

### 方案 1：在 Windows 上启动（推荐）

如果您在 Windows 上开发，请使用 Windows 的目录：

```bash
cd C:\development\claudetask-test\claudetask\backend
python run.py
```

### 方案 2：在 WSL 中启动

1. **安装依赖**（如果使用系统 Python）：
   ```bash
   cd /mnt/c/development/claudetask/backend
   python3 -m pip install --user flask flask-cors flask-socketio bcrypt requests
   ```

2. **或者重建虚拟环境**：
   ```bash
   cd /mnt/c/development/claudetask/backend
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **运行应用**：
   ```bash
   python run.py
   # 或
   python3 run.py
   ```

### 方案 3：快速启动（无虚拟环境）

直接运行修复脚本：
```bash
cd /mnt/c/development/claudetask/backend
python3 fix_and_run.py
```

## 登录账号

默认管理员账号：
- **邮箱**: `admin@claudetask.local`
- **密码**: `admin123`

或创建新的管理员账号：
```bash
python3 create_admin.py
```
这会创建 `admin@sparticle.com` / `admin123`

## 验证服务是否运行

1. 后端应该监听在 `http://localhost:5000`
2. 前端访问 `http://localhost:3000`
3. 查看后端控制台是否有错误输出

## 常见问题

### Q: ModuleNotFoundError: No module named 'flask'
A: Flask 未安装，运行 `python3 -m pip install flask`

### Q: sqlite3.OperationalError: no such column: value
A: 数据库表结构问题，已通过代码自动修复

### Q: Address already in use
A: 端口 5000 被占用，检查是否有其他 Flask 实例在运行

### Q: 登录时仍然 500 错误
A: 查看后端控制台的具体错误信息，可能是：
- 数据库连接问题
- 导入错误
- 配置问题

## 调试建议

1. **查看后端日志**：
   ```bash
   tail -f *.log
   ```

2. **运行诊断脚本**：
   ```bash
   python3 diagnose.py
   ```

3. **测试登录**：
   ```bash
   python3 test_login.py
   ```

## 紧急方案

如果以上都不行，使用简化的测试服务器：
```bash
python3 test_server.py
```
这会启动一个最小化的登录服务用于测试。