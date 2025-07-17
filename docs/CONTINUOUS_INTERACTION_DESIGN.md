# 🔄 持续交互设计方案

本文档描述了两种实现 Claude Task 持续交互的方案设计。

## 📋 背景

当前问题：
- Claude 在 Web 环境中无法处理需要用户交互的任务
- 单个任务执行完成后，上下文会丢失
- 无法处理多步骤的复杂任务

## 🚀 方案1：启动本地工具继续执行

### 架构设计

```
Web界面 → 任务创建 → 生成脚本 → 启动本地CLI → 结果同步
```

### 实现细节

#### 1. 任务脚本生成器

```python
# backend/services/script_generator.py
class TaskScriptGenerator:
    def generate_claude_script(self, task):
        """生成可在本地执行的 Claude 脚本"""
        script_content = f"""#!/bin/bash
# Claude Task Script
# Task ID: {task.id}
# Created: {datetime.now()}

cd "{task.project_path}"

# 执行 Claude 命令
claude "{task.prompt}"

# 保存结果
echo "Task completed. Press Enter to close..."
read
"""
        return script_content
    
    def generate_windows_batch(self, task):
        """生成 Windows 批处理文件"""
        batch_content = f"""@echo off
REM Claude Task Script
REM Task ID: {task.id}

cd /d "{task.project_path}"
claude "{task.prompt}"
pause
"""
        return batch_content
```

#### 2. 本地启动器

```python
# backend/services/local_launcher.py
import platform
import subprocess

class LocalLauncher:
    def launch_terminal_with_script(self, script_path):
        """启动终端并执行脚本"""
        system = platform.system()
        
        if system == "Windows":
            # Windows Terminal 或 CMD
            subprocess.Popen([
                'wt', '-w', '0', 'new-tab', 
                'cmd', '/k', script_path
            ])
        elif system == "Darwin":
            # macOS Terminal
            subprocess.Popen([
                'open', '-a', 'Terminal', script_path
            ])
        else:
            # Linux
            subprocess.Popen([
                'x-terminal-emulator', '-e', 
                f'bash {script_path}'
            ])
```

#### 3. API 端点

```python
# backend/routes/api.py
@app.route('/api/tasks/<task_id>/launch-local', methods=['POST'])
def launch_local_execution(task_id):
    """启动本地执行"""
    task = Task.query.get(task_id)
    
    # 生成脚本
    generator = TaskScriptGenerator()
    script_content = generator.generate_claude_script(task)
    
    # 保存脚本
    script_path = f"temp/task_{task_id}.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    os.chmod(script_path, 0o755)
    
    # 启动本地终端
    launcher = LocalLauncher()
    launcher.launch_terminal_with_script(script_path)
    
    return jsonify({"status": "launched", "script": script_path})
```

#### 4. 前端集成

```jsx
// frontend/src/components/LocalExecutionButton.jsx
const LocalExecutionButton = ({ taskId }) => {
  const handleLaunchLocal = async () => {
    try {
      await api.post(`/api/tasks/${taskId}/launch-local`);
      message.success('已启动本地终端执行任务');
    } catch (error) {
      message.error('启动失败');
    }
  };
  
  return (
    <Button 
      icon={<DesktopOutlined />}
      onClick={handleLaunchLocal}
    >
      在本地终端执行
    </Button>
  );
};
```

## 🔗 方案2：父子任务系统

### 架构设计

```
父任务 → 创建子任务 → 继承上下文 → 自动执行 → 结果聚合
```

### 实现细节

#### 1. 数据库模型更新

```python
# backend/models/task.py
class Task(db.Model):
    # 现有字段...
    parent_task_id = db.Column(db.String(36), db.ForeignKey('task.id'))
    children = db.relationship('Task', backref=db.backref('parent', remote_side=[id]))
    context = db.Column(db.Text)  # 存储任务上下文
    sequence_order = db.Column(db.Integer)  # 执行顺序
    
    def create_child_task(self, prompt, inherit_context=True):
        """创建子任务"""
        child = Task(
            prompt=prompt,
            project_path=self.project_path,
            parent_task_id=self.id,
            context=self.context if inherit_context else None,
            sequence_order=len(self.children) + 1
        )
        return child
```

#### 2. 任务链执行器

```python
# backend/services/task_chain_executor.py
class TaskChainExecutor:
    def __init__(self, executor):
        self.executor = executor
        
    def execute_chain(self, parent_task):
        """执行任务链"""
        # 执行父任务
        self.executor.execute(
            parent_task.prompt,
            parent_task.project_path,
            completion_callback=lambda t: self._on_parent_complete(t)
        )
    
    def _on_parent_complete(self, parent_task):
        """父任务完成后，自动执行子任务"""
        children = sorted(parent_task.children, key=lambda t: t.sequence_order)
        
        for child in children:
            # 构建包含上下文的提示
            contextual_prompt = self._build_contextual_prompt(child, parent_task)
            
            self.executor.execute(
                contextual_prompt,
                child.project_path,
                completion_callback=lambda t: self._on_child_complete(t)
            )
    
    def _build_contextual_prompt(self, child_task, parent_task):
        """构建包含上下文的提示"""
        context = f"""
基于之前的任务结果继续执行：
上一个任务：{parent_task.prompt}
上一个任务输出摘要：{self._summarize_output(parent_task.output)}

当前任务：{child_task.prompt}

请基于上述上下文继续执行当前任务。
"""
        return context
```

#### 3. 任务模板系统

```javascript
// frontend/src/utils/taskTemplates.js
export const chainedTaskTemplates = [
  {
    name: "完整功能开发",
    tasks: [
      {
        prompt: "创建项目结构和基础配置文件",
        order: 1
      },
      {
        prompt: "实现核心功能模块",
        order: 2
      },
      {
        prompt: "添加单元测试",
        order: 3
      },
      {
        prompt: "创建文档",
        order: 4
      }
    ]
  },
  {
    name: "代码审查和优化",
    tasks: [
      {
        prompt: "分析代码质量并生成报告",
        order: 1
      },
      {
        prompt: "根据报告进行代码优化",
        order: 2
      },
      {
        prompt: "运行测试确保功能正常",
        order: 3
      }
    ]
  }
];
```

#### 4. 前端任务链创建界面

```jsx
// frontend/src/components/TaskChainCreator.jsx
const TaskChainCreator = ({ projectPath }) => {
  const [tasks, setTasks] = useState([{ prompt: '', order: 1 }]);
  
  const addTask = () => {
    setTasks([...tasks, { prompt: '', order: tasks.length + 1 }]);
  };
  
  const createTaskChain = async () => {
    const response = await api.post('/api/task-chains', {
      project_path: projectPath,
      tasks: tasks
    });
    
    message.success('任务链创建成功，开始执行...');
  };
  
  return (
    <Card title="创建任务链">
      {tasks.map((task, index) => (
        <div key={index}>
          <TextArea
            value={task.prompt}
            onChange={(e) => updateTask(index, e.target.value)}
            placeholder={`任务 ${index + 1}`}
            rows={3}
          />
        </div>
      ))}
      <Button onClick={addTask}>添加子任务</Button>
      <Button type="primary" onClick={createTaskChain}>
        创建并执行任务链
      </Button>
    </Card>
  );
};
```

## 📊 方案对比

| 特性 | 方案1：本地工具 | 方案2：父子任务 |
|-----|--------------|--------------|
| 交互能力 | ✅ 完整支持 | ❌ 仍受限制 |
| 实现复杂度 | 中等 | 较高 |
| 用户体验 | 需要切换窗口 | 统一界面 |
| 跨平台 | 需要适配 | ✅ 天然支持 |
| 任务追踪 | 较难 | ✅ 容易 |
| 上下文传递 | 需要额外处理 | ✅ 自动支持 |

## 🎯 推荐实现路径

### 第一阶段：实现方案2（父子任务）
1. 更新数据库模型支持任务关系
2. 实现任务链执行器
3. 创建任务链管理界面
4. 添加上下文传递机制

### 第二阶段：实现方案1（本地工具）
1. 创建脚本生成器
2. 实现跨平台终端启动
3. 添加结果同步机制
4. 提供一键切换选项

### 第三阶段：混合方案
1. 智能判断任务类型
2. 简单任务使用父子系统
3. 交互任务启动本地工具
4. 统一的任务管理界面

## 🔧 技术要点

### 1. 上下文管理
```python
class ContextManager:
    def extract_key_info(self, output):
        """从输出中提取关键信息"""
        # 提取文件创建信息
        # 提取错误信息
        # 提取状态变更
        pass
    
    def build_context(self, previous_tasks):
        """构建上下文信息"""
        # 汇总之前的任务信息
        # 生成简洁的上下文描述
        pass
```

### 2. 任务依赖管理
```python
class TaskDependencyManager:
    def can_execute(self, task):
        """检查任务是否可以执行"""
        # 检查父任务是否完成
        # 检查依赖条件
        pass
    
    def get_next_tasks(self, completed_task):
        """获取下一个要执行的任务"""
        # 根据完成状态决定下一步
        pass
```

## 🚦 实施建议

1. **先实现基础的父子任务系统**
   - 支持创建子任务
   - 简单的上下文传递
   - 顺序执行

2. **逐步增强功能**
   - 条件执行
   - 并行任务
   - 错误处理和重试

3. **最后添加本地执行**
   - 作为高级选项
   - 主要用于复杂交互场景

## 📝 总结

两种方案各有优势，建议：
1. 优先实现父子任务系统，解决大部分连续执行需求
2. 将本地工具执行作为补充，处理特殊场景
3. 长期目标是创建一个智能的混合系统，自动选择最佳执行方式