import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Progress, Table, Typography, Space, Tag, Spin, Alert } from 'antd'
import { TrophyOutlined, RobotOutlined, ClockCircleOutlined, ProjectOutlined, RiseOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { taskApi, authApi } from '../services/api'
import '../styles/Dashboard.css'

const { Title, Text } = Typography

const Dashboard = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState(null)
  const [agentMetrics, setAgentMetrics] = useState(null)
  const [monthlyRankings, setMonthlyRankings] = useState([])

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // 获取当前用户
      const userData = await authApi.getCurrentUser()
      setCurrentUser(userData.user)
      
      // 获取Agent指标
      const metricsData = await taskApi.getAgentMetrics()
      setAgentMetrics(metricsData.user_metrics)
      setMonthlyRankings(metricsData.monthly_rankings || [])
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatHours = (hours) => {
    if (hours < 1) {
      return `${Math.round(hours * 60)} 分钟`
    } else if (hours < 24) {
      return `${hours.toFixed(1)} 小时`
    } else {
      const days = Math.floor(hours / 24)
      const remainingHours = (hours % 24).toFixed(1)
      return `${days} 天 ${remainingHours} 小时`
    }
  }

  const getAgentLoadColor = (load) => {
    if (load < 20) return '#ff4d4f'  // 红色 - 低负荷
    if (load < 60) return '#faad14'  // 橙色 - 中等负荷
    if (load < 80) return '#52c41a'  // 绿色 - 良好负荷
    return '#1890ff'  // 蓝色 - 高负荷
  }

  const getAgentLoadStatus = (load) => {
    if (load < 20) return 'exception'
    if (load < 60) return 'normal'
    if (load < 80) return 'success'
    return 'active'
  }

  const rankingColumns = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
      render: (rank) => {
        if (rank === 1) return <Tag color="gold"><TrophyOutlined /> 第一名</Tag>
        if (rank === 2) return <Tag color="silver">第二名</Tag>
        if (rank === 3) return <Tag color="orange">第三名</Tag>
        return `第${rank}名`
      }
    },
    {
      title: '用户',
      dataIndex: 'user_email',
      key: 'user_email',
      render: (email, record) => (
        <Space>
          <Text>{email || record.user_id}</Text>
          {record.user_id === currentUser?.id && <Tag color="blue">你</Tag>}
        </Space>
      )
    },
    {
      title: 'Agent负荷',
      dataIndex: 'agent_load',
      key: 'agent_load',
      render: (load) => (
        <Progress
          percent={Math.min(load, 100)}
          size="small"
          strokeColor={getAgentLoadColor(load)}
          format={(percent) => `${percent}%`}
        />
      )
    },
    {
      title: '本月时长',
      dataIndex: 'total_hours',
      key: 'total_hours',
      render: (hours) => formatHours(hours)
    },
    {
      title: '任务数',
      dataIndex: 'total_tasks',
      key: 'total_tasks',
    }
  ]

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    )
  }

  const currentMonth = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' })

  return (
    <div className="dashboard-container">
      <Title level={2}>
        <Space>
          <RobotOutlined />
          Agent 生产力仪表板
        </Space>
      </Title>
      
      <Alert
        message="Agent负荷说明"
        description="1个满负荷Agent = 7×24×30 = 5,040小时/月。Agent负荷反映了您的AI助手利用率。"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Row gutter={[16, 16]}>
        {/* 个人Agent负荷卡片 */}
        <Col xs={24} md={12} lg={8}>
          <Card
            title={
              <Space>
                <RobotOutlined />
                我的Agent负荷
              </Space>
            }
            extra={<Tag color="blue">{currentMonth}</Tag>}
          >
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="dashboard"
                percent={Math.min(agentMetrics?.agent_load || 0, 100)}
                width={200}
                strokeColor={getAgentLoadColor(agentMetrics?.agent_load || 0)}
                status={getAgentLoadStatus(agentMetrics?.agent_load || 0)}
                format={(percent) => (
                  <div>
                    <div style={{ fontSize: 32, fontWeight: 'bold' }}>{percent}%</div>
                    <div style={{ fontSize: 14, color: '#999' }}>Agent负荷</div>
                  </div>
                )}
              />
              <div style={{ marginTop: 16 }}>
                <Text type="secondary">
                  本月已使用 {formatHours(agentMetrics?.total_hours || 0)}
                </Text>
              </div>
            </div>
          </Card>
        </Col>

        {/* 排名信息 */}
        <Col xs={24} md={12} lg={8}>
          <Card
            title={
              <Space>
                <TrophyOutlined />
                当月排名
              </Space>
            }
          >
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="公司内排名"
                  value={agentMetrics?.rank || '-'}
                  prefix="#"
                  valueStyle={{ color: agentMetrics?.rank <= 3 ? '#cf1322' : '#3f8600' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="本月任务数"
                  value={agentMetrics?.total_tasks || 0}
                  prefix={<ProjectOutlined />}
                />
              </Col>
              <Col span={24}>
                <Statistic
                  title="累积总时长"
                  value={formatHours(agentMetrics?.cumulative_hours || 0)}
                  prefix={<ClockCircleOutlined />}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 快速操作 */}
        <Col xs={24} md={12} lg={8}>
          <Card
            title={
              <Space>
                <RiseOutlined />
                快速操作
              </Space>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Card
                size="small"
                hoverable
                onClick={() => navigate('/projects')}
                style={{ cursor: 'pointer' }}
              >
                <Space>
                  <ProjectOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                  <div>
                    <div style={{ fontWeight: 'bold' }}>项目管理</div>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      创建和管理项目
                    </Text>
                  </div>
                </Space>
              </Card>
              
              <Card
                size="small"
                hoverable
                onClick={() => navigate('/tasks')}
                style={{ cursor: 'pointer' }}
              >
                <Space>
                  <ClockCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                  <div>
                    <div style={{ fontWeight: 'bold' }}>任务历史</div>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      查看所有任务记录
                    </Text>
                  </div>
                </Space>
              </Card>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 月度排行榜 */}
      <Card
        title={
          <Space>
            <TrophyOutlined />
            本月Agent负荷排行榜
          </Space>
        }
        style={{ marginTop: 16 }}
      >
        <Table
          columns={rankingColumns}
          dataSource={monthlyRankings}
          rowKey="user_id"
          pagination={false}
          size="middle"
          rowClassName={(record) => record.user_id === currentUser?.id ? 'highlight-row' : ''}
        />
      </Card>
    </div>
  )
}

export default Dashboard