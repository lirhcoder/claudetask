import React from 'react';
import { Steps, Card, Tag, Progress, Space } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined, ClockCircleOutlined } from '@ant-design/icons';

const TaskChainProgress = ({ parentTask, children = [] }) => {
  if (!parentTask || parentTask.task_type !== 'parent') {
    return null;
  }

  const getTaskStatus = (task) => {
    switch (task.status) {
      case 'completed':
        return {
          status: 'finish',
          icon: <CheckCircleOutlined />,
          color: 'success'
        };
      case 'failed':
        return {
          status: 'error',
          icon: <CloseCircleOutlined />,
          color: 'error'
        };
      case 'running':
        return {
          status: 'process',
          icon: <LoadingOutlined />,
          color: 'processing'
        };
      default:
        return {
          status: 'wait',
          icon: <ClockCircleOutlined />,
          color: 'default'
        };
    }
  };

  const allTasks = [parentTask, ...children];
  const completedCount = allTasks.filter(t => t.status === 'completed').length;
  const progress = Math.round((completedCount / allTasks.length) * 100);

  return (
    <Card size="small" title="任务链进度" style={{ marginBottom: 16 }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Progress 
          percent={progress} 
          status={parentTask.status === 'failed' ? 'exception' : 'active'}
        />
        
        <Steps
          current={allTasks.findIndex(t => t.status === 'running')}
          direction="vertical"
          size="small"
        >
          {allTasks.map((task, index) => {
            const statusInfo = getTaskStatus(task);
            return (
              <Steps.Step
                key={task.id}
                title={
                  <Space>
                    {index === 0 ? '父任务' : `子任务 ${index}`}
                    <Tag color={statusInfo.color} style={{ marginLeft: 8 }}>
                      {task.status}
                    </Tag>
                  </Space>
                }
                description={task.prompt.substring(0, 50) + '...'}
                status={statusInfo.status}
                icon={statusInfo.icon}
              />
            );
          })}
        </Steps>
      </Space>
    </Card>
  );
};

export default TaskChainProgress;