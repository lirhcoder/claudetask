import React, { useState, useEffect } from 'react'
import { Table, Tag, Button, Space, message, Tooltip } from 'antd'
import { ReloadOutlined, EyeOutlined, StopOutlined } from '@ant-design/icons'
import { taskApi } from '../services/api'
import TaskDetailModal from '../components/TaskDetailModal'

const TasksPage = () => {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedTask, setSelectedTask] = useState(null)
  const [modalVisible, setModalVisible] = useState(false)

  useEffect(() => {
    loadTasks()
  }, [])

  const loadTasks = async () => {
    try {
      setLoading(true)
      const data = await taskApi.listTasks()
      setTasks(data.tasks)
    } catch (error) {
      message.error('Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }

  const handleCancelTask = async (taskId) => {
    try {
      await taskApi.cancelTask(taskId)
      message.success('Task cancelled')
      loadTasks()
    } catch (error) {
      message.error('Failed to cancel task')
    }
  }

  const handleViewTask = (task) => {
    setSelectedTask(task)
    setModalVisible(true)
  }

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

  const columns = [
    {
      title: 'Task ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      ellipsis: true,
      render: (id) => (
        <Tooltip title={id}>
          <span>{id.substring(0, 8)}...</span>
        </Tooltip>
      )
    },
    {
      title: 'Prompt',
      dataIndex: 'prompt',
      key: 'prompt',
      ellipsis: true,
      render: (prompt) => (
        <Tooltip title={prompt}>
          <span>{prompt.length > 50 ? prompt.substring(0, 50) + '...' : prompt}</span>
        </Tooltip>
      )
    },
    {
      title: 'Project',
      dataIndex: 'project_path',
      key: 'project_path',
      width: 200,
      ellipsis: true,
      render: (path) => path.split('/').pop()
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: getStatusTag
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      render: (duration) => duration ? `${duration.toFixed(2)}s` : '-'
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date) => new Date(date).toLocaleString()
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleViewTask(record)}
            size="small"
          />
          {record.status === 'running' && (
            <Button
              type="text"
              danger
              icon={<StopOutlined />}
              onClick={() => handleCancelTask(record.id)}
              size="small"
            />
          )}
        </Space>
      )
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Task History</h1>
        <Button
          icon={<ReloadOutlined />}
          onClick={loadTasks}
          loading={loading}
        >
          Refresh
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={tasks}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} tasks`
        }}
      />

      <TaskDetailModal
        task={selectedTask}
        visible={modalVisible}
        onClose={() => {
          setModalVisible(false)
          setSelectedTask(null)
        }}
      />
    </div>
  )
}

export default TasksPage