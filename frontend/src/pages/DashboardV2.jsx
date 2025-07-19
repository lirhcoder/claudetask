import React, { useState, useEffect } from 'react';
import { Layout, Card, Row, Col, Statistic, Button, List, Space, Tag, Empty, Spin } from 'antd';
import {
  RocketOutlined,
  FolderOutlined,
  CheckCircleOutlined,
  ThunderboltOutlined,
  PlusOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { unifiedApi } from '../services/api';

const { Content } = Layout;

const DashboardV2 = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState({
    repositories: [],
    recent_tasks: [],
    stats: {
      total_repos: 0,
      active_tasks: 0,
      completed_today: 0
    },
    quick_actions: []
  });

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const data = await unifiedApi.getDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (actionId) => {
    switch (actionId) {
      case 'create_task':
        navigate('/repositories');
        break;
      case 'view_repos':
        navigate('/repositories');
        break;
      case 'settings':
        navigate('/settings');
        break;
      default:
        break;
    }
  };

  const getStatusColor = (status) => {
    const statusMap = {
      'in_progress': 'processing',
      'completed': 'success',
      'failed': 'error',
      'draft': 'default'
    };
    return statusMap[status] || 'default';
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>工作台</h1>

        {/* 统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} md={8}>
            <Card hoverable onClick={() => navigate('/repositories')}>
              <Statistic
                title="仓库总数"
                value={dashboardData.stats.total_repos}
                prefix={<FolderOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card>
              <Statistic
                title="进行中任务"
                value={dashboardData.stats.active_tasks}
                prefix={<RocketOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card>
              <Statistic
                title="今日完成"
                value={dashboardData.stats.completed_today}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]}>
          {/* 快捷操作 */}
          <Col xs={24} md={8} lg={6}>
            <Card title="快捷操作" style={{ height: '100%' }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                {dashboardData.quick_actions.map(action => (
                  <Button
                    key={action.id}
                    block
                    size="large"
                    icon={
                      action.icon === 'plus' ? <PlusOutlined /> :
                      action.icon === 'folder' ? <FolderOutlined /> :
                      action.icon === 'setting' ? <SettingOutlined /> :
                      <ThunderboltOutlined />
                    }
                    onClick={() => handleQuickAction(action.id)}
                  >
                    {action.label}
                  </Button>
                ))}
              </Space>
            </Card>
          </Col>

          {/* 最近任务 */}
          <Col xs={24} md={16} lg={18}>
            <Card 
              title="最近任务" 
              extra={<a onClick={() => navigate('/repositories')}>查看全部</a>}
            >
              {dashboardData.recent_tasks.length === 0 ? (
                <Empty
                  description="暂无任务"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                >
                  <Button type="primary" onClick={() => navigate('/repositories')}>
                    去创建
                  </Button>
                </Empty>
              ) : (
                <List
                  dataSource={dashboardData.recent_tasks}
                  renderItem={task => (
                    <List.Item
                      actions={[
                        <Button
                          type="link"
                          onClick={() => navigate(`/repository/${task.repository_id}`)}
                        >
                          查看
                        </Button>
                      ]}
                    >
                      <List.Item.Meta
                        title={
                          <Space>
                            <span>{task.title}</span>
                            <Tag color={getStatusColor(task.status)}>
                              {task.status === 'in_progress' ? '执行中' :
                               task.status === 'completed' ? '已完成' :
                               task.status === 'failed' ? '失败' : '待执行'}
                            </Tag>
                          </Space>
                        }
                        description={
                          <Space style={{ fontSize: 12, color: '#999' }}>
                            <span>{task.repository}</span>
                            <span>•</span>
                            <span>{new Date(task.created_at).toLocaleDateString()}</span>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              )}
            </Card>
          </Col>
        </Row>
    </div>
  );
};

export default DashboardV2;