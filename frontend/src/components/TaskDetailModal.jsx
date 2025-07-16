import React from 'react'
import { Modal, Descriptions, Tag, Typography } from 'antd'

const { Text, Paragraph } = Typography

const TaskDetailModal = ({ task, visible, onClose }) => {
  if (!task) return null

  const getStatusTag = (status) => {
    const statusConfig = {
      pending: { color: 'default', text: 'Pending' },
      running: { color: 'processing', text: 'Running' },
      completed: { color: 'success', text: 'Completed' },
      failed: { color: 'error', text: 'Failed' },
      cancelled: { color: 'warning', text: 'Cancelled' }
    }
    
    const config = statusConfig[status] || statusConfig.pending
    return <Tag color={config.color}>{config.text}</Tag>
  }

  return (
    <Modal
      title="Task Details"
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      <Descriptions bordered column={1}>
        <Descriptions.Item label="Task ID">
          <Text code>{task.id}</Text>
        </Descriptions.Item>
        <Descriptions.Item label="Status">
          {getStatusTag(task.status)}
        </Descriptions.Item>
        <Descriptions.Item label="Project Path">
          {task.project_path}
        </Descriptions.Item>
        <Descriptions.Item label="Created At">
          {new Date(task.created_at).toLocaleString()}
        </Descriptions.Item>
        {task.started_at && (
          <Descriptions.Item label="Started At">
            {new Date(task.started_at).toLocaleString()}
          </Descriptions.Item>
        )}
        {task.completed_at && (
          <Descriptions.Item label="Completed At">
            {new Date(task.completed_at).toLocaleString()}
          </Descriptions.Item>
        )}
        {task.duration && (
          <Descriptions.Item label="Duration">
            {task.duration.toFixed(2)} seconds
          </Descriptions.Item>
        )}
        {task.exit_code !== null && task.exit_code !== undefined && (
          <Descriptions.Item label="Exit Code">
            <Tag color={task.exit_code === 0 ? 'success' : 'error'}>
              {task.exit_code}
            </Tag>
          </Descriptions.Item>
        )}
        <Descriptions.Item label="Prompt">
          <Paragraph style={{ marginBottom: 0 }}>
            {task.prompt}
          </Paragraph>
        </Descriptions.Item>
        {task.error && (
          <Descriptions.Item label="Error">
            <Text type="danger">{task.error}</Text>
          </Descriptions.Item>
        )}
      </Descriptions>
      
      {task.output && (
        <div style={{ marginTop: 16 }}>
          <h4>Output:</h4>
          <div
            style={{
              background: '#f5f5f5',
              padding: 12,
              borderRadius: 4,
              maxHeight: 400,
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: 12,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}
          >
            {task.output}
          </div>
        </div>
      )}
    </Modal>
  )
}

export default TaskDetailModal