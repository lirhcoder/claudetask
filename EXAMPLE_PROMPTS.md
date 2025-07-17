# 📝 示例提示词集合

本文档包含各种场景的示例提示词，帮助你更好地与 Claude 交互。

## 1. 处理开发文档（如 HTML to SVG to PPT 工具）

### ❌ 错误示例
```
I've completed creating a comprehensive development document for your HTML to SVG to PPT conversion tool...
```
问题：只是告诉你创建了文档，但没有说明要保存在哪里。

### ✅ 正确示例
```
创建 HTML to SVG to PPT 转换工具的开发文档，并保存到 docs/DEVELOPMENT.md 文件。

文档应包含：
1. 项目概述
2. 技术架构
3. 核心模块
4. API 设计
5. 实现细节
6. 部署指南
7. 使用说明
8. 开发路线图

【文件操作要求】
- 直接使用 Write 工具创建文件
- 保存路径：docs/DEVELOPMENT.md
- 如果 docs 目录不存在，先创建目录
- 如果文件已存在，直接覆盖
```

## 2. 创建项目文件结构

### ✅ 正确示例
```
为 Python Web API 项目创建标准的项目结构。

【自动化要求】
1. 创建以下目录结构：
   - src/ - 源代码目录
   - tests/ - 测试目录
   - docs/ - 文档目录
   - config/ - 配置文件目录
   
2. 创建必要的文件：
   - README.md - 项目说明
   - requirements.txt - 依赖列表
   - .gitignore - Git 忽略文件
   - src/__init__.py - Python 包标识
   - src/main.py - 主程序入口
   
3. 文件操作规则：
   - 直接创建所有文件和目录
   - 不要询问确认
   - 使用标准的 Python 项目模板
```

## 3. 实现完整功能

### ✅ 正确示例
```
实现一个文件上传和处理系统，包括前端和后端。

【技术要求】
- 后端：FastAPI + Python
- 前端：React + TypeScript
- 文件存储：本地文件系统

【自动化实现要求】
1. 后端实现：
   - 创建 backend/app.py - FastAPI 应用主文件
   - 创建 backend/routes/upload.py - 上传路由
   - 创建 backend/services/file_processor.py - 文件处理服务
   - 自动添加必要的依赖到 requirements.txt

2. 前端实现：
   - 创建 frontend/src/components/FileUpload.tsx - 上传组件
   - 创建 frontend/src/services/api.ts - API 服务
   - 更新 package.json 添加必要的依赖

3. 执行规则：
   - 直接创建所有文件
   - 选择合适的文件上传库（如 multer）
   - 实现错误处理和进度显示
   - 完成后运行测试确保功能正常
```

## 4. 代码重构

### ✅ 正确示例
```
重构 src/utils 目录下的所有工具函数，提取公共逻辑并优化性能。

【重构规则】
1. 文件处理：
   - 直接修改现有文件
   - 创建新的公共模块 src/utils/common.js
   - 更新所有引用

2. 优化策略：
   - 识别重复代码并提取
   - 使用更高效的算法
   - 添加适当的缓存机制

3. 自动化要求：
   - 不询问确认，直接执行
   - 重构后自动运行测试
   - 保持 API 兼容性
```

## 5. 批量操作

### ✅ 正确示例
```
将项目中所有的 console.log 语句替换为使用 winston 日志库。

【批量处理规则】
1. 安装依赖：
   - 自动运行 npm install winston
   - 更新 package.json

2. 创建日志配置：
   - 创建 src/config/logger.js 配置文件
   - 设置不同环境的日志级别

3. 批量替换：
   - 扫描所有 .js 和 .ts 文件
   - 将 console.log → logger.info
   - 将 console.error → logger.error
   - 将 console.warn → logger.warn

4. 执行要求：
   - 自动处理所有文件
   - 添加必要的 import 语句
   - 完成后运行代码确保无错误
```

## 6. Git 操作

### ✅ 正确示例
```
完成功能开发后，创建新分支并提交代码。

【Git 自动化流程】
1. 创建功能分支：
   - 分支名：feature/user-authentication
   - 基于：main 分支

2. 提交更改：
   - 自动添加所有相关文件
   - 提交信息：feat: 实现用户认证功能
   - 包含详细的更改说明

3. 推送到远程：
   - 自动推送到 origin
   - 设置上游分支

4. 执行规则：
   - 不需要任何确认
   - 如有冲突，保留两边更改
   - 完成后显示分支状态
```

## 7. 文档生成

### ✅ 正确示例
```
为项目生成完整的 API 文档，保存到 docs/API.md。

【文档生成要求】
1. 扫描所有 API 端点
2. 提取路由、参数、响应格式
3. 生成 Markdown 格式文档
4. 包含使用示例

【文件操作】
- 保存位置：docs/API.md
- 直接创建文件，不要只显示内容
- 如果目录不存在，自动创建
- 包含目录索引和锚点链接
```

## 8. 测试创建

### ✅ 正确示例
```
为 src/services/userService.js 创建完整的单元测试。

【测试创建规则】
1. 测试文件位置：
   - 创建 tests/services/userService.test.js
   - 使用项目现有的测试框架（Jest/Mocha）

2. 测试内容：
   - 覆盖所有公共方法
   - 包含正常和异常情况
   - 模拟外部依赖

3. 执行要求：
   - 直接创建测试文件
   - 自动运行测试验证
   - 确保覆盖率 > 80%
```

## 💡 提示词编写要点

1. **明确文件路径**：始终指定文件的保存位置
2. **使用具体动词**：用"创建"、"保存"、"写入"而不是"生成"、"展示"
3. **包含操作指令**：明确要求使用 Write 工具
4. **预设所有决策**：不要让 Claude 询问选择
5. **完整的上下文**：提供足够的信息让 Claude 能自主完成任务

## 🚫 避免的模式

- "请展示..." → 改为 "请创建并保存到..."
- "生成代码" → 改为 "创建文件 [路径] 并写入代码"
- "是否需要..." → 改为 "直接执行..."
- "你觉得..." → 改为 "使用 [具体方案]..."