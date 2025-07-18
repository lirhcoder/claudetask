# 登录问题解决方案

## 问题诊断

您遇到的 500 错误是由于后端 Flask 应用在启动时，`system_config` 表结构不正确导致的。

## 解决步骤

### 1. 使用正确的管理员账号登录

根据数据库中的实际数据，有以下账号可用：

**管理员账号：**
- 邮箱：`admin@claudetask.local`  
- 密码：`admin123`

**普通用户账号：**
- 邮箱：`test.auto@sparticle.com`
- 邮箱：`rh.li@sparticle.com`

### 2. 如果需要创建 admin@sparticle.com 账号

在后端目录运行：
```bash
cd backend
python3 create_admin.py
```

### 3. 修复 system_config 表问题

问题已经通过更新 `models/config.py` 解决。代码会自动检测并修复旧的表结构。

### 4. 如果仍有问题，手动修复数据库

```bash
cd backend
python3 fix_config_table.py
```

### 5. 启动后端服务

```bash
cd backend
python3 run.py
```

或者在 Windows 上：
```bash
cd backend
python run.py
```

## 验证步骤

1. 确保后端服务正常运行（应该看到 Flask 启动信息）
2. 在浏览器中访问前端
3. 使用上述账号登录

## 常见问题

**Q: 仍然收到 500 错误**  
A: 检查后端控制台输出，查看具体错误信息

**Q: 忘记密码**  
A: 运行 `python3 create_admin.py` 重置管理员密码

**Q: 需要不同的管理员邮箱**  
A: 修改 `create_admin.py` 中的邮箱地址，然后运行它