import React, { useState } from 'react';
import { Card, Button, Input, Space, message, Modal, List, Tag, Tooltip, Row, Col } from 'antd';
import { PlusOutlined, DeleteOutlined, PlayCircleOutlined, LinkOutlined, OrderedListOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { taskApi } from '../services/api';

const { TextArea } = Input;

const TaskChainCreator = ({ projectPath, onChainCreated }) => {
  const [visible, setVisible] = useState(false);
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([
    { prompt: '', order: 1, description: '初始任务' }
  ]);
  const [executing, setExecuting] = useState(false);

  // 预设的任务链模板
  const chainTemplates = [
    {
      name: '完整功能开发',
      icon: <OrderedListOutlined />,
      tasks: [
        { prompt: '分析需求并创建项目结构', description: '需求分析' },
        { prompt: '实现核心功能模块', description: '功能开发' },
        { prompt: '编写单元测试和集成测试', description: '测试编写' },
        { prompt: '创建使用文档和API文档', description: '文档编写' }
      ]
    },
    {
      name: '代码优化流程',
      icon: <LinkOutlined />,
      tasks: [
        { prompt: '分析代码质量，识别性能瓶颈和代码异味', description: '代码分析' },
        { prompt: '基于分析结果进行代码重构和优化', description: '代码优化' },
        { prompt: '运行测试确保功能正常，更新受影响的文档', description: '验证更新' }
      ]
    }
  ];

  const addTask = () => {
    const newTask = {
      prompt: '',
      order: tasks.length + 1,
      description: `子任务 ${tasks.length}`
    };
    setTasks([...tasks, newTask]);
  };

  const updateTask = (index, field, value) => {
    const updated = [...tasks];
    updated[index][field] = value;
    setTasks(updated);
  };

  const removeTask = (index) => {
    if (tasks.length <= 1) {
      message.warning('至少需要保留一个任务');
      return;
    }
    
    const updated = tasks.filter((_, i) => i !== index);
    // 重新编号
    updated.forEach((task, i) => {
      task.order = i + 1;
      if (i > 0) {
        task.description = task.description || `子任务 ${i}`;
      }
    });
    setTasks(updated);
  };

  const loadTemplate = (template) => {
    Modal.confirm({
      title: '加载模板',
      content: `确定要加载"${template.name}"模板吗？当前的任务将被替换。`,
      onOk: () => {
        setTasks(template.tasks.map((t, i) => ({
          ...t,
          order: i + 1
        })));
        message.success('模板已加载');
      }
    });
  };

  const validateTasks = () => {
    for (let i = 0; i < tasks.length; i++) {
      if (!tasks[i].prompt.trim()) {
        message.error(`任务 ${i + 1} 的提示语不能为空`);
        return false;
      }
    }
    return true;
  };

  const createAndExecute = async () => {
    if (!validateTasks()) return;

    setExecuting(true);
    try {
      const taskData = {
        project_path: projectPath,
        tasks: tasks.map(t => ({ prompt: t.prompt }))
      };
      
      console.log('Creating task chain with data:', taskData);
      const response = await taskApi.createTaskChain(taskData);
      
      console.log('Task chain response:', response);

      message.success('任务链创建成功，开始执行...');
      setVisible(false);
      setTasks([{ prompt: '', order: 1, description: '初始任务' }]);
      
      if (onChainCreated) {
        // 检查响应数据格式
        const responseData = response.data || response;
        console.log('Passing data to onChainCreated:', responseData);
        onChainCreated(responseData);
      }
      
      // 跳转到任务一览页面
      navigate('/tasks');
    } catch (error) {
      console.error('创建任务链失败:', error);
      console.error('Error response:', error.response);
      message.error(error.response?.data?.error || error.message || '创建任务链失败');
    } finally {
      setExecuting(false);
    }
  };

  return (
    <>
      <Button
        type="primary"
        icon={<LinkOutlined />}
        onClick={() => setVisible(true)}
      >
        创建任务链
      </Button>

      <Modal
        title="创建任务链"
        open={visible}
        onCancel={() => setVisible(false)}
        width={800}
        footer={[
          <Button key="cancel" onClick={() => setVisible(false)}>
            取消
          </Button>,
          <Button
            key="execute"
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={createAndExecute}
            loading={executing}
          >
            创建并执行
          </Button>
        ]}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* 模板选择 */}
          <Card size="small" title="快速模板">
            <Space>
              {chainTemplates.map((template, index) => (
                <Button
                  key={index}
                  icon={template.icon}
                  onClick={() => loadTemplate(template)}
                >
                  {template.name}
                </Button>
              ))}
            </Space>
          </Card>

          {/* 任务列表 */}
          <Card size="small" title="任务序列">
            <List
              dataSource={tasks}
              renderItem={(task, index) => (
                <List.Item
                  actions={[
                    <Tooltip title="删除任务">
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => removeTask(index)}
                        disabled={tasks.length === 1}
                      />
                    </Tooltip>
                  ]}
                >
                  <div style={{ width: '100%' }}>
                    <Row gutter={8} align="middle">
                      <Col span={2}>
                        <Tag color={index === 0 ? 'blue' : 'green'}>
                          {index === 0 ? '父任务' : `子任务${index}`}
                        </Tag>
                      </Col>
                      <Col span={22}>
                        <TextArea
                          value={task.prompt}
                          onChange={(e) => updateTask(index, 'prompt', e.target.value)}
                          placeholder={`输入${task.description}的提示语...`}
                          rows={2}
                          style={{ marginBottom: 8 }}
                        />
                        <Input
                          value={task.description}
                          onChange={(e) => updateTask(index, 'description', e.target.value)}
                          placeholder="任务描述（可选）"
                          size="small"
                        />
                      </Col>
                    </Row>
                  </div>
                </List.Item>
              )}
            />
            
            <Button
              type="dashed"
              onClick={addTask}
              icon={<PlusOutlined />}
              style={{ width: '100%', marginTop: 16 }}
            >
              添加子任务
            </Button>
          </Card>

          {/* 说明 */}
          <Card size="small" title="使用说明">
            <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
              <li>父任务完成后会自动执行所有子任务</li>
              <li>子任务会继承父任务的上下文信息</li>
              <li>每个子任务都能看到之前任务的执行结果</li>
              <li>如果某个任务失败，后续任务将不会执行</li>
              <li>建议在提示语中使用非交互模式指令</li>
            </ul>
          </Card>
        </Space>
      </Modal>
    </>
  );
};

export default TaskChainCreator;