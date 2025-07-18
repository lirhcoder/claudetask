# 后端启动指南

## 问题说明
当前遇到的问题是 Flask 依赖没有正确安装在系统中。

## 临时解决方案
我已经启动了一个简单的测试服务器在端口 5000 上运行，它可以：
- 响应登录请求 (使用 admin@sparticle.com / admin123)
- 提供基本的 API 响应

## 正式解决方案

### 选项 1：在 Windows 上安装依赖
如果您在 Windows 上有 Python 环境：
```bash
# 在 Windows PowerShell 或 CMD 中
cd C:\development\claudetask\backend
pip install -r requirements.txt
python app.py
```

### 选项 2：使用 Docker
创建一个 Dockerfile：
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### 选项 3：修复 WSL 环境
在 WSL 中安装 pip：
```bash
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt
python3 app.py
```

## 当前状态
- 测试服务器正在运行：http://localhost:5000
- 可以使用以下凭据登录：
  - 邮箱：admin@sparticle.com
  - 密码：admin123

## 停止测试服务器
```bash
# 找到进程 ID
ps aux | grep test_server
# 杀死进程
kill <PID>
```