# 本地执行结果同步

## 概述
本地终端执行功能现在支持将执行结果自动同步回 Web 界面。无论任务是正常完成还是被用户中断（Ctrl+C），结果都会被捕获并上传。

## 工作原理

### 1. 执行流程
```
Web 界面 → 创建任务 → 启动本地终端 → Python 执行器 → Claude Code → 捕获输出 → 上传结果 → 更新 Web 界面
```

### 2. 核心组件

#### claude_executor.py
- 包装 Claude Code 执行
- 实时捕获输出到文件
- 处理 Ctrl+C 中断信号
- 记录执行时间和退出代码
- 自动上传结果到服务器

#### result_uploader.py
- 创建结果 JSON 文件
- 通过 HTTP API 上传结果
- 处理网络错误和重试

#### API 端点: /api/tasks/<task_id>/local-result
- 接收本地执行结果
- 更新任务状态和输出
- 通过 WebSocket 通知前端

### 3. 结果数据结构
```json
{
  "task_id": "任务ID",
  "status": "completed|failed|cancelled",
  "output": "执行输出内容",
  "completed_at": "完成时间",
  "exit_code": 0,
  "duration": 123.45,
  "interrupted": false
}
```

## 功能特性

### 支持的场景
1. **正常完成** - 任务执行成功，exit_code = 0
2. **执行失败** - 任务执行失败，exit_code != 0
3. **用户中断** - 用户按 Ctrl+C，interrupted = true
4. **网络断开** - 结果保存在本地，稍后可手动上传

### 输出捕获
- 实时捕获 stdout 和 stderr
- 保留完整的执行日志
- 支持 UTF-8 编码
- 自动处理编码错误

### 状态同步
- 实时更新任务状态
- WebSocket 推送更新
- 前端自动刷新显示

## 使用方法

### 1. 启动本地执行
```javascript
// 前端代码
await taskApi.executeLocal(prompt, projectPath)
```

### 2. 监控执行状态
- Web 界面会显示"等待本地执行结果"
- 执行完成后自动更新显示结果

### 3. 中断执行
- 在终端窗口按 Ctrl+C
- 结果会标记为"cancelled"
- Web 界面显示"任务已中断"

## 配置选项

### 环境变量
- `API_BASE_URL` - API 服务器地址，默认 http://localhost:5000

### 临时文件
- 输出文件: `temp/task_{id}_output.txt`
- 结果文件: `temp/task_{id}_result.json`

## 故障排除

### 结果未同步
1. 检查服务器是否运行
2. 确认网络连接正常
3. 查看本地 temp 目录是否有结果文件

### 编码错误
- Windows 系统已自动处理 UTF-8 编码
- 如仍有问题，检查系统区域设置

### 上传失败
- 结果会保存在本地
- 可以手动调用 upload_task_result 函数重试