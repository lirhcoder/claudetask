# 🎯 Claude Task 提示词最佳实践

本文档帮助你编写能让 Claude 无需任何交互即可持续工作的提示词。

## 📋 核心原则

### 1. 明确的非交互指令
在提示词中始终包含明确的非交互指令，告诉 Claude 不要询问确认。

### 2. 预设所有决策
为所有可能的选择场景预设决策规则，避免 Claude 需要询问。

### 3. 完整的错误处理
指定错误处理方式，让 Claude 能够自主处理异常情况。

### 4. 明确的文件操作
始终指定文件的保存路径，要求使用 Write 工具实际创建文件，而不是只展示内容。

## 🚀 提示词模板

### 基础模板
```
[具体任务描述]

【非交互模式指令】
1. 不要询问任何确认，直接执行所有操作
2. 文件操作：如果文件已存在，直接覆盖；如果目录不存在，递归创建
3. 选择处理：遇到多个选项时，选择最合适或第一个可用的选项
4. 错误处理：遇到非致命错误时，记录错误并继续执行，不要中断
5. 默认行为：所有操作使用默认配置，不要等待用户输入
6. 持续执行：完成一个任务后，自动继续下一个任务，直到全部完成
```

### 文件操作专用
```
创建或修改以下文件：[文件列表]

文件操作规则：
- 明确指定保存路径（如 docs/DEVELOPMENT.md, src/main.py）
- 使用 Write 工具实际创建文件，不要只显示内容
- 如果文件已存在，直接覆盖，不要询问
- 如果目录不存在，自动创建所有必需的父目录
- 使用 UTF-8 编码保存所有文件
- 创建后自动格式化代码（如果适用）

示例：
❌ "生成开发文档" 
✅ "创建开发文档并保存到 docs/DEVELOPMENT.md"
```

### 代码开发专用
```
实现功能：[功能描述]

开发规则：
- 自主选择最佳实现方案，不要询问技术选型
- 自动创建所需的文件和目录结构
- 遵循项目现有的代码风格和命名规范
- 完成后自动运行测试（如果存在）
- 发现问题时自动修复，不要等待确认
```

### Git 操作专用
```
执行 Git 操作：[操作描述]

Git 自动化规则：
- 自动添加相关文件到暂存区
- 使用描述性的提交信息
- 如有冲突，优先保留两边的更改
- 不需要确认，直接执行 push
- 如果需要，自动创建新分支
```

## 💡 常见场景示例

### 1. 创建完整功能
```
创建一个用户认证系统，包括登录、注册和密码重置功能。

【完全自动化要求】
- 自动创建所有必需的文件（模型、控制器、视图、路由）
- 选择合适的加密算法（bcrypt）
- 自动创建数据库迁移文件
- 添加必要的中间件和验证
- 创建相应的单元测试
- 如遇到任何选择，使用行业最佳实践
- 完成后运行测试确保功能正常
```

### 2. 重构代码
```
重构 components 目录下的所有 React 组件，提取公共逻辑。

【自动化重构规则】
- 识别重复代码并自动提取为公共函数或组件
- 保持原有功能不变
- 自动更新所有引用
- 使用 TypeScript 添加类型定义
- 重构后自动运行测试
- 发现测试失败时自动修复
```

### 3. 批量处理
```
将所有 .js 文件转换为 .ts 文件，并添加类型定义。

【批量处理规则】
- 自动处理所有匹配的文件
- 推断并添加适当的类型定义
- 保留原有功能和逻辑
- 处理导入导出语句
- 跳过已经是 TypeScript 的文件
- 完成一个文件后立即处理下一个
```

## ⚠️ 注意事项

### 避免的词汇
- "请问..."
- "是否需要..."
- "您想要..."
- "应该选择哪个..."
- "确认一下..."

### 推荐的词汇
- "直接执行..."
- "自动处理..."
- "使用默认..."
- "选择最优..."
- "不需要确认..."

## 🔧 调试技巧

如果任务仍然因交互而失败：

1. **检查日志**：查看后端日志中的交互检测警告
2. **使用优化器**：点击"优化"按钮自动改进提示词
3. **添加更多指令**：在提示词中添加更具体的非交互指令
4. **使用模板**：从预设模板开始，然后根据需要修改

## 📚 进阶技巧

### 1. 链式任务
```
完成以下任务序列：
1. 创建项目结构
2. 实现核心功能
3. 添加测试
4. 优化性能
5. 更新文档

链式执行规则：
- 按顺序执行，每个任务完成后自动开始下一个
- 如果某个任务失败，记录错误但继续执行后续任务
- 最后提供所有任务的执行摘要
```

### 2. 条件执行
```
检查并修复代码中的问题。

条件规则：
- 如果发现 TypeScript 错误，自动修复
- 如果发现未使用的导入，自动删除
- 如果发现格式问题，自动格式化
- 如果测试覆盖率低于 80%，自动添加测试
```

### 3. 智能决策
```
优化项目性能。

智能决策规则：
- 分析性能瓶颈，选择最有效的优化方案
- 如果是前端项目，优先考虑包大小和加载时间
- 如果是后端项目，优先考虑响应时间和并发能力
- 根据项目类型自动选择合适的优化工具
```

## 🎯 总结

编写好的非交互提示词的关键是：
1. **预见所有可能的交互点**
2. **提供明确的决策规则**
3. **使用肯定、直接的语言**
4. **包含完整的错误处理指令**
5. **测试并根据反馈优化**

记住：Claude 需要明确的指令才能自主工作。你提供的指令越详细、越明确，执行成功率就越高。