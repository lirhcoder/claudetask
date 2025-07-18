import React from 'react'
import { Card, Progress, Button, Space, Typography, Tag, Tooltip, Row, Col, Statistic } from 'antd'
import {
  FolderOpenOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  EyeOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import '../styles/ProjectCard.css'

const { Text, Title } = Typography

const ProjectCard = ({ project, onDelete, onCreateTask }) => {
  const navigate = useNavigate()
  
  // 计算进度百分比
  const calculateProgress = () => {
    const stats = project.task_stats
    if (!stats || stats.total === 0) return 0
    return Math.round((stats.completed / stats.total) * 100)
  }
  
  // 获取进度条颜色
  const getProgressStatus = () => {
    const stats = project.task_stats
    if (!stats || stats.total === 0) return 'normal'
    if (stats.failed > 0) return 'exception'
    if (stats.completed === stats.total) return 'success'
    if (stats.running > 0) return 'active'
    return 'normal'
  }
  
  // 跳转到任务列表（带过滤）
  const navigateToTasks = (status) => {
    const params = new URLSearchParams()
    params.set('project', project.name)
    if (status && status !== 'all') {
      params.set('status', status)
    }
    navigate(`/tasks?${params.toString()}`)
  }
  
  // 渲染任务统计
  const renderTaskStats = () => {
    const stats = project.task_stats || {
      total: 0,
      pending: 0,
      running: 0,
      completed: 0,
      failed: 0,
      cancelled: 0
    }
    
    const StatisticWrapper = ({ children, onClick, disabled }) => (
      <div 
        onClick={disabled ? undefined : onClick}
        style={{ 
          cursor: disabled ? 'default' : 'pointer',
          transition: 'all 0.3s',
          borderRadius: '4px',
          padding: '4px'
        }}
        className={disabled ? '' : 'statistic-clickable'}
      >
        {children}
      </div>
    )
    
    return (
      <Row gutter={16}>
        <Col span={6}>
          <StatisticWrapper onClick={() => navigateToTasks('all')} disabled={stats.total === 0}>
            <Statistic
              title="总任务"
              value={stats.total}
              valueStyle={{ fontSize: '20px' }}
              prefix={<ClockCircleOutlined />}
            />
          </StatisticWrapper>
        </Col>
        <Col span={6}>
          <StatisticWrapper onClick={() => navigateToTasks('running')} disabled={stats.running === 0}>
            <Statistic
              title="运行中"
              value={stats.running}
              valueStyle={{ fontSize: '20px', color: '#1890ff' }}
              prefix={<PlayCircleOutlined />}
            />
          </StatisticWrapper>
        </Col>
        <Col span={6}>
          <StatisticWrapper onClick={() => navigateToTasks('completed')} disabled={stats.completed === 0}>
            <Statistic
              title="已完成"
              value={stats.completed}
              valueStyle={{ fontSize: '20px', color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </StatisticWrapper>
        </Col>
        <Col span={6}>
          <StatisticWrapper onClick={() => navigateToTasks('failed')} disabled={stats.failed === 0}>
            <Statistic
              title="失败"
              value={stats.failed}
              valueStyle={{ fontSize: '20px', color: stats.failed > 0 ? '#ff4d4f' : undefined }}
              prefix={<CloseCircleOutlined />}
            />
          </StatisticWrapper>
        </Col>
      </Row>
    )
  }
  
  const handleViewProject = () => {
    navigate(`/project/${project.name}`)
  }
  
  const handleCreateTask = () => {
    if (onCreateTask) {
      onCreateTask(project)
    } else {
      // 默认行为：跳转到项目页面
      navigate(`/project/${project.name}`)
    }
  }
  
  const roleMap = {
    'owner': { text: '所有者', color: 'gold' },
    'admin': { text: '管理员', color: 'blue' },
    'viewer': { text: '查看者', color: 'green' }
  }
  const roleInfo = roleMap[project.role] || { text: project.role, color: 'default' }
  
  return (
    <Card
      hoverable
      className="project-card"
      style={{ height: '100%' }}
      actions={[
        <Tooltip title="新建任务" key="create">
          <Button
            type="text"
            icon={<PlusOutlined />}
            onClick={handleCreateTask}
            style={{ color: '#1890ff' }}
          >
            新任务
          </Button>
        </Tooltip>,
        <Tooltip title="查看详情" key="view">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={handleViewProject}
          >
            详情
          </Button>
        </Tooltip>,
        <Tooltip title="删除项目" key="delete">
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => onDelete(project.name)}
            disabled={project.role && project.role !== 'owner'}
          >
            删除
          </Button>
        </Tooltip>
      ]}
    >
      <Card.Meta
        avatar={<FolderOpenOutlined style={{ fontSize: '32px', color: '#1890ff' }} />}
        title={
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <Title level={5} style={{ margin: 0 }}>{project.name}</Title>
              <Tag color={roleInfo.color}>{roleInfo.text}</Tag>
            </Space>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {new Date(project.modified_at).toLocaleString('zh-CN')}
            </Text>
          </Space>
        }
      />
      
      <div className="project-card-stats">
        {renderTaskStats()}
      </div>
      
      <div className="project-card-progress">
        <Text type="secondary">任务进度</Text>
        <Progress
          percent={calculateProgress()}
          status={getProgressStatus()}
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
          format={percent => {
            const stats = project.task_stats
            if (!stats || stats.total === 0) return '暂无任务'
            return `${percent}%`
          }}
        />
        {project.task_stats && project.task_stats.pending > 0 && (
          <Space 
            style={{ marginTop: '8px', cursor: 'pointer' }}
            onClick={() => navigateToTasks('pending')}
          >
            <ExclamationCircleOutlined style={{ color: '#faad14' }} />
            <Text type="secondary" style={{ textDecoration: 'underline' }}>
              {project.task_stats.pending} 个任务待处理
            </Text>
          </Space>
        )}
      </div>
    </Card>
  )
}

export default ProjectCard