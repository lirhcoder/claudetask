import React, { useState, useEffect } from 'react'
import { Table, Tag, Button, Space, message, Tooltip, Badge, Input, Select } from 'antd'
import { ReloadOutlined, EyeOutlined, StopOutlined, SyncOutlined, SearchOutlined, ClearOutlined, UserOutlined } from '@ant-design/icons'
import { useSearchParams } from 'react-router-dom'
import { taskApi } from '../services/api'
import TaskDetailModal from '../components/TaskDetailModal'

const TasksPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [tasks, setTasks] = useState([])
  const [filteredTasks, setFilteredTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedTask, setSelectedTask] = useState(null)
  const [modalVisible, setModalVisible] = useState(false)
  const [, forceUpdate] = useState({})
  const [settings, setSettings] = useState({
    taskPageAutoRefresh: false,
    taskPageRefreshInterval: 5
  })
  
  // 从URL参数初始化过滤条件
  const [searchText, setSearchText] = useState(searchParams.get('search') || '')
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || 'all')
  const [userFilter, setUserFilter] = useState(searchParams.get('user') || '')
  const [projectFilter, setProjectFilter] = useState(searchParams.get('project') || '')
  const [currentUser, setCurrentUser] = useState(null)

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
      console.log('Settings updated:', event.detail)
      setSettings(prev => ({ ...prev, ...event.detail }))
    }

    window.addEventListener('settings-updated', handleSettingsUpdate)
    return () => {
      window.removeEventListener('settings-updated', handleSettingsUpdate)
    }
  }, [])

  // 初次加载任务和用户信息
  useEffect(() => {
    loadTasks()
    loadCurrentUser()
  }, [])

  const loadCurrentUser = async () => {
    try {
      const { authApi } = await import('../services/api')
      const response = await authApi.getCurrentUser()
      setCurrentUser(response.user)
    } catch (error) {
      console.error('Failed to load user info:', error)
    }
  }

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

  // 当任务列表更新时，重新应用过滤器
  useEffect(() => {
    filterTasks(tasks, searchText, statusFilter, userFilter, projectFilter)
  }, [tasks])
  
  // 当URL参数变化时更新状态
  useEffect(() => {
    const status = searchParams.get('status') || 'all'
    const search = searchParams.get('search') || ''
    const user = searchParams.get('user') || ''
    const project = searchParams.get('project') || ''
    
    setStatusFilter(status)
    setSearchText(search)
    setUserFilter(user)
    setProjectFilter(project)
    
    filterTasks(tasks, search, status, user, project)
  }, [searchParams])

  const loadTasks = async () => {
    try {
      setLoading(true)
      const data = await taskApi.listTasks()
      setTasks(data.tasks)
      // 应用当前的过滤器
      filterTasks(data.tasks, searchText, statusFilter, userFilter, projectFilter)
    } catch (error) {
      message.error('Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }

  // 过滤任务
  const filterTasks = (taskList, search, status, user, project) => {
    let filtered = [...taskList]
    
    // 状态过滤
    if (status !== 'all') {
      filtered = filtered.filter(task => task.status === status)
    }
    
    // 用户过滤
    if (user) {
      const userLower = user.toLowerCase()
      filtered = filtered.filter(task => {
        const taskUser = task.user_email || task.user_id || ''
        return taskUser.toLowerCase().includes(userLower)
      })
    }
    
    // 项目过滤
    if (project) {
      const projectLower = project.toLowerCase()
      filtered = filtered.filter(task => {
        const taskPath = task.project_path || ''
        // 检查项目路径是否包含项目名
        return taskPath.toLowerCase().includes(projectLower) || 
               taskPath.toLowerCase().endsWith('/' + projectLower)
      })
    }
    
    // 文本搜索（搜索ID、提示词、项目路径）
    if (search) {
      const searchLower = search.toLowerCase()
      filtered = filtered.filter(task => {
        return (
          task.id.toLowerCase().includes(searchLower) ||
          task.prompt.toLowerCase().includes(searchLower) ||
          task.project_path.toLowerCase().includes(searchLower)
        )
      })
    }
    
    setFilteredTasks(filtered)
  }

  // 更新URL参数
  const updateURLParams = (updates) => {
    const newParams = new URLSearchParams(searchParams)
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value && value !== 'all') {
        newParams.set(key, value)
      } else {
        newParams.delete(key)
      }
    })
    
    setSearchParams(newParams)
  }

  // 处理搜索框变化
  const handleSearch = (value) => {
    setSearchText(value)
    filterTasks(tasks, value, statusFilter, userFilter, projectFilter)
    updateURLParams({ search: value })
  }

  // 处理状态过滤器变化
  const handleStatusFilter = (value) => {
    setStatusFilter(value)
    filterTasks(tasks, searchText, value, userFilter, projectFilter)
    updateURLParams({ status: value })
  }

  // 处理用户过滤器变化
  const handleUserFilter = (value) => {
    setUserFilter(value)
    filterTasks(tasks, searchText, statusFilter, value, projectFilter)
    updateURLParams({ user: value })
  }

  // 清除所有过滤条件
  const clearAllFilters = () => {
    setSearchText('')
    setStatusFilter('all')
    setUserFilter('')
    setProjectFilter('')
    filterTasks(tasks, '', 'all', '', '')
    setSearchParams(new URLSearchParams())
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
      title: '用户',
      dataIndex: 'user_email',
      key: 'user_email',
      width: 150,
      ellipsis: true,
      render: (email, record) => {
        const displayUser = email || record.user_id || '未知用户'
        return (
          <Tooltip title={displayUser}>
            <span>{displayUser === currentUser?.email ? '我' : displayUser}</span>
          </Tooltip>
        )
      }
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
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
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
        
        <Space style={{ width: '100%', marginBottom: 16 }} size="middle" wrap>
          <Input
            placeholder="搜索任务ID、提示词或项目名称..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => handleSearch(e.target.value)}
            style={{ width: 300 }}
            allowClear
          />
          <Select
            value={statusFilter}
            onChange={handleStatusFilter}
            style={{ width: 150 }}
            options={[
              { value: 'all', label: '全部状态' },
              { value: 'pending', label: 'Pending' },
              { value: 'running', label: 'Running' },
              { value: 'completed', label: 'Completed' },
              { value: 'failed', label: 'Failed' },
              { value: 'cancelled', label: 'Cancelled' }
            ]}
          />
          <Input
            placeholder="过滤用户..."
            prefix={<UserOutlined />}
            value={userFilter}
            onChange={(e) => handleUserFilter(e.target.value)}
            style={{ width: 200 }}
            allowClear
          />
          <Button
            icon={<ClearOutlined />}
            onClick={clearAllFilters}
            disabled={!searchText && statusFilter === 'all' && !userFilter && !projectFilter}
          >
            清除过滤
          </Button>
          <span style={{ color: '#666' }}>
            共 {filteredTasks.length} 个任务
            {searchText || statusFilter !== 'all' || userFilter || projectFilter ? ` (总计 ${tasks.length} 个)` : ''}
          </span>
          {projectFilter && (
            <Tag 
              closable 
              onClose={() => {
                setProjectFilter('')
                filterTasks(tasks, searchText, statusFilter, userFilter, '')
                updateURLParams({ project: '' })
              }}
              color="blue"
            >
              项目: {projectFilter}
            </Tag>
          )}
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={filteredTasks}
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