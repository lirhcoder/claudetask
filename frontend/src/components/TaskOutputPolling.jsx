import React, { useState, useEffect, useRef } from 'react';
import { Card, Empty, Spin } from 'antd';
import { taskApi } from '../services/api';

const TaskOutputPolling = ({ task }) => {
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [taskStatus, setTaskStatus] = useState(task?.status || 'pending');
  const outputRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!task?.id) return;

    // 开始轮询
    const pollInterval = parseInt(import.meta.env.VITE_POLLING_INTERVAL || '2000');
    
    const pollTask = async () => {
      try {
        const updatedTask = await taskApi.getTask(task.id);
        setOutput(updatedTask.output || '');
        setTaskStatus(updatedTask.status);
        
        // 如果任务完成，停止轮询
        if (['completed', 'failed', 'cancelled'].includes(updatedTask.status)) {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        }
      } catch (error) {
        console.error('Failed to poll task:', error);
      }
    };

    // 立即执行一次
    pollTask();
    
    // 如果任务还在运行，设置轮询
    if (!['completed', 'failed', 'cancelled'].includes(taskStatus)) {
      intervalRef.current = setInterval(pollTask, pollInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [task?.id]);

  useEffect(() => {
    // 自动滚动到底部
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  if (!task) {
    return (
      <Empty description="No task selected" />
    );
  }

  const getStatusColor = () => {
    switch (taskStatus) {
      case 'completed': return '#52c41a';
      case 'failed': return '#ff4d4f';
      case 'running': return '#1890ff';
      case 'cancelled': return '#faad14';
      default: return '#d9d9d9';
    }
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ 
        padding: '8px', 
        background: '#f0f2f5', 
        borderBottom: '1px solid #d9d9d9',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span>Task ID: {task.id}</span>
        <span style={{ color: getStatusColor() }}>
          {taskStatus === 'running' && <Spin size="small" style={{ marginRight: 8 }} />}
          Status: {taskStatus}
        </span>
      </div>
      
      <div 
        ref={outputRef}
        style={{ 
          flex: 1,
          padding: '12px',
          fontFamily: 'Consolas, Monaco, monospace',
          fontSize: '13px',
          lineHeight: '1.5',
          background: '#1e1e1e',
          color: '#d4d4d4',
          overflow: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all'
        }}
      >
        {output || (loading ? 'Loading output...' : 'No output yet...')}
      </div>
      
      {taskStatus === 'running' && (
        <div style={{ 
          padding: '8px', 
          background: '#f0f2f5', 
          borderTop: '1px solid #d9d9d9',
          fontSize: '12px',
          color: '#8c8c8c',
          textAlign: 'center'
        }}>
          轮询模式 - 每 {import.meta.env.VITE_POLLING_INTERVAL || '2000'}ms 更新
        </div>
      )}
    </div>
  );
};

export default TaskOutputPolling;