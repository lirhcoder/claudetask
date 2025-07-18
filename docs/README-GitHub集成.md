# ClaudeTask GitHub 集成功能

## 🚀 新功能

ClaudeTask 现已支持 GitHub 集成，实现了完整的代码开发工作流：

- **仓库 = GitHub 仓库**：管理代码项目
- **分支 = AI 任务**：每个分支对应一个开发任务
- **议题 = 子任务**：细分的开发步骤

## 📝 快速使用

### 1. 导入 GitHub 仓库

1. 进入"仓库管理"页面
2. 点击"导入 GitHub 仓库"
3. 输入仓库地址（如 `https://github.com/facebook/react`）
4. 系统自动克隆并创建本地仓库

### 2. 创建分支执行任务

1. 进入仓库详情
2. 新建分支，填写任务描述
3. 点击"执行"，AI 自动完成编码

### 3. 同步 GitHub

点击"同步 GitHub"按钮，更新：
- 最新的分支列表
- 议题状态
- 仓库统计信息

## 🔑 配置访问令牌（可选）

访问私有仓库需要设置 GitHub Token：

```bash
# Linux/Mac
export GITHUB_ACCESS_TOKEN=your_token

# Windows
set GITHUB_ACCESS_TOKEN=your_token
```

## 📊 功能对照表

| ClaudeTask | GitHub | 说明 |
|------------|--------|------|
| 仓库 | Repository | 代码项目 |
| 分支 | Branch | AI 执行的任务 |
| 议题 | Issue | 待完成的子任务 |
| 执行 | - | AI 自动编码 |
| 同步 | Pull/Push | 代码同步 |

## 🎯 使用场景

1. **Bug 修复**
   - 导入项目 → 创建修复分支 → AI 修复 → 创建 PR

2. **功能开发**
   - 创建功能分支 → 分解为多个议题 → AI 逐步实现

3. **代码重构**
   - 创建重构分支 → AI 分析并重构 → 测试并提交

## ⚠️ 注意事项

- 公开仓库无需 Token
- API 限制：60次/小时（无 Token）、5000次/小时（有 Token）
- 确保已安装 Git

## 🛠️ 问题排查

**Q: 导入失败？**
A: 检查仓库 URL 和访问权限

**Q: 同步失败？**
A: 确认网络连接和 Token 设置

**Q: Git 操作失败？**
A: 运行 `git --version` 确认 Git 已安装