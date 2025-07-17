import React, { useState, useEffect } from 'react';
import { Tag, Alert, Spin, Space, Typography } from 'antd';
import { SyncOutlined, CheckCircleOutlined, CloseCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';

const { Text } = Typography;

const LocalExecutionStatus = ({ task, isLocalExecution = false }) => {
  const [syncStatus, setSyncStatus] = useState('unknown');
  const [lastSyncTime, setLastSyncTime] = useState(null);
  
  useEffect(() => {
    if (!task || !isLocalExecution) return;
    
    // 检查任务状态以确定同步状态
    if (task.status === 'running') {
      setSyncStatus('waiting');
    } else if (task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled') {
      setSyncStatus('synced');
      setLastSyncTime(task.completed_at);
    }
  }, [task, isLocalExecution]);
  
  if (!isLocalExecution) return null;
  
  const getStatusTag = () => {
    switch (syncStatus) {
      case 'waiting':
        return (
          <Tag icon={<SyncOutlined spin />} color="processing">
            等待本地执行结果
          </Tag>
        );
      case 'synced':
        return (
          <Tag icon={<CheckCircleOutlined />} color="success">
            结果已同步
          </Tag>
        );
      case 'error':
        return (
          <Tag icon={<CloseCircleOutlined />} color="error">
            同步失败
          </Tag>
        );
      default:
        return (
          <Tag icon={<PauseCircleOutlined />} color="default">
            未知状态
          </Tag>
        );
    }
  };
  
  const getAlertMessage = () => {
    if (syncStatus === 'waiting') {
      return (
        <Alert
          message="本地执行中"
          description={
            <Space direction="vertical" size="small">
              <Text>任务正在本地终端中执行...</Text>
              <Text type="secondary">
                执行结束后（正常完成或用户中断），结果将自动同步到此处。
              </Text>
            </Space>
          }
          type="info"
          showIcon
          icon={<Spin size="small" />}
        />
      );
    }
    
    if (syncStatus === 'synced' && task.status === 'cancelled') {
      return (
        <Alert
          message="任务已中断"
          description="用户在本地终端中中断了任务执行 (Ctrl+C)"
          type="warning"
          showIcon
        />
      );
    }
    
    return null;
  };
  
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Space>
        <Text strong>同步状态:</Text>
        {getStatusTag()}
        {lastSyncTime && (
          <Text type="secondary" style={{ fontSize: '12px' }}>
            同步时间: {new Date(lastSyncTime).toLocaleString('zh-CN')}
          </Text>
        )}
      </Space>
      {getAlertMessage()}
    </Space>
  );
};

export default LocalExecutionStatus;