import React, { useState, useEffect } from 'react'
import { Table, Tag, Button, Space, message, Tooltip, Badge } from 'antd'
import { ReloadOutlined, EyeOutlined, StopOutlined, SyncOutlined } from '@ant-design/icons'
import { taskApi } from '../services/api'
import TaskDetailModal from '../components/TaskDetailModal'

const TasksPage = () => {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedTask, setSelectedTask] = useState(null)
  const [modalVisible, setModalVisible] = useState(false)
  const [, forceUpdate] = useState({})
  const [settings, setSettings] = useState({
    taskPageAutoRefresh: true,
    taskPageRefreshInterval: 5
  })

  // 格式化持续时间
  const formatDuration = (seconds) => {
    if (!seconds || seconds < 0) return '-'
    
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    
    if (hours > 0) {
      return `${hours}小时${minutes}分${secs}秒`
    } else if (minutes > 0) {
      return `${minutes}分${secs}秒`
    } else {
      return `${secs}秒`
    }
  }

  // 计算实时持续时间
  const calculateDuration = (task) => {
    if (task.status === 'pending') return '-'
    
    if (task.status === 'running') {
      // 正在运行的任务，计算从开始到现在的时间
      const startTime = task.started_at ? new Date(task.started_at) : new Date(task.created_at)
      const duration = (Date.now() - startTime.getTime()) / 1000
      return formatDuration(duration)
    }
    
    // 已完成的任务
    if (task.execution_time) {
      return formatDuration(task.execution_time)
    } else if (task.completed_at && (task.started_at || task.created_at)) {
      const startTime = task.started_at ? new Date(task.started_at) : new Date(task.created_at)
      const endTime = new Date(task.completed_at)
      const duration = (endTime.getTime() - startTime.getTime()) / 1000
      return formatDuration(duration)
    }
    
    return '-'
  }

  // 加载设置
  useEffect(() => {
    const loadSettings = () => {
      const savedSettings = localStorage.getItem('claudetask_settings')
      if (savedSettings) {
        try {
          const parsedSettings = JSON.parse(savedSettings)
          setSettings(prev => ({ ...prev, ...parsedSettings }))
        } catch (e) {
          console.error('加载设置失败:', e)
        }
      }
    }

    loadSettings()

    // 监听设置更新事件
    const handleSettingsUpdate = (event) => {
      setSettings(prev => ({ ...prev, ...event.detail }))
    }

    window.addEventListener('settings-updated', handleSettingsUpdate)
    return () => {
      window.removeEventListener('settings-updated', handleSettingsUpdate)
    }
  }, [])

  // 初次加载任务
  useEffect(() => {
    loadTasks()
  }, [])

  // 处理自动刷新
  useEffect(() => {
    let interval = null

    // 任务列表自动刷新
    if (settings.taskPageAutoRefresh) {
      interval = setInterval(() => {
        loadTasks()
      }, settings.taskPageRefreshInterval * 1000)
    }
    
    // 清理定时器
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [settings.taskPageAutoRefresh, settings.taskPageRefreshInterval])

  // 持续时间显示更新（固定每秒更新）
  useEffect(() => {
    const durationInterval = setInterval(() => {
      // 如果有正在运行的任务，强制更新组件以刷新时间显示
      if (tasks.some(task => task.status === 'running')) {
        forceUpdate({})
      }
    }, 1000)
    
    return () => clearInterval(durationInterval)
  }, [tasks])

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
      render: (_, record) => calculateDuration(record)
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
        <Space>
          {settings.taskPageAutoRefresh && (
            <Badge 
              dot 
              color="green"
              title={`自动刷新: 每${settings.taskPageRefreshInterval}秒`}
            >
              <SyncOutlined style={{ color: '#52c41a' }} />
            </Badge>
          )}
          <Button
            icon={<ReloadOutlined />}
            onClick={loadTasks}
            loading={loading}
          >
            Refresh
          </Button>
        </Space>
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