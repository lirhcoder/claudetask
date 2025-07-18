import React, { useState, useEffect } from 'react';
import { Layout, Card, Row, Col, Statistic, Table, Tabs, Progress, Tag, Button, Radio, Spin, message } from 'antd';
import {
  TrophyOutlined,
  RiseOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  UserOutlined,
  CrownOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import axios from 'axios';
import { Line } from '@ant-design/charts';
import './AgentIndexPage.css';

const { Content } = Layout;
const { TabPane } = Tabs;

const AgentIndexPage = () => {
  const [loading, setLoading] = useState(false);
  const [myMetrics, setMyMetrics] = useState(null);
  const [rankings, setRankings] = useState([]);
  const [period, setPeriod] = useState('monthly');
  const [userHistory, setUserHistory] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [companyStats, setCompanyStats] = useState(null);

  useEffect(() => {
    loadMyMetrics();
    loadRankings('monthly');
  }, []);

  const loadMyMetrics = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/agent/metrics');
      setMyMetrics(response.data);
      
      // 检查是否是管理员
      const authResponse = await axios.get('/api/auth/me');
      setIsAdmin(authResponse.data.user.is_admin);
      
      // 加载历史数据
      if (response.data.user_metrics?.user_id) {
        loadUserHistory(response.data.user_metrics.user_id);
      }
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const loadRankings = async (periodType) => {
    try {
      const response = await axios.get(`/api/agent/rankings?period=${periodType}`);
      setRankings(response.data.rankings);
    } catch (error) {
      message.error('加载排行榜失败');
    }
  };

  const loadUserHistory = async (userId) => {
    try {
      const response = await axios.get(`/api/agent/history/${userId}?months=6`);
      setUserHistory(response.data.history.reverse());
    } catch (error) {
      console.error('加载历史数据失败', error);
    }
  };

  const loadCompanyStats = async () => {
    if (!isAdmin) return;
    
    try {
      const response = await axios.get('/api/agent/company-stats');
      setCompanyStats(response.data);
    } catch (error) {
      message.error('加载公司统计失败');
    }
  };

  const handlePeriodChange = (e) => {
    const newPeriod = e.target.value;
    setPeriod(newPeriod);
    loadRankings(newPeriod);
  };

  const formatEmployeeIndex = (index) => {
    return (index * 100).toFixed(2) + '%';
  };

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1:
        return <CrownOutlined style={{ color: '#FFD700', fontSize: 20 }} />;
      case 2:
        return <TrophyOutlined style={{ color: '#C0C0C0', fontSize: 18 }} />;
      case 3:
        return <TrophyOutlined style={{ color: '#CD7F32', fontSize: 16 }} />;
      default:
        return rank;
    }
  };

  // 排行榜列配置
  const rankingColumns = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
      render: (rank) => getRankIcon(rank)
    },
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      render: (username, record) => (
        <div>
          <div>{username}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.email}</div>
        </div>
      )
    },
    {
      title: '工作时长',
      dataIndex: 'total_hours',
      key: 'total_hours',
      render: (hours) => `${hours.toFixed(1)} 小时`
    },
    {
      title: '任务数',
      dataIndex: 'total_tasks',
      key: 'total_tasks'
    },
    {
      title: '员工指数',
      dataIndex: 'employee_index',
      key: 'employee_index',
      render: (index) => (
        <Progress
          percent={index * 100}
          format={(percent) => `${percent.toFixed(2)}%`}
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
        />
      )
    }
  ];

  // 历史趋势图配置
  const historyConfig = {
    data: userHistory.map(item => ({
      month: item.month,
      value: item.index * 100,
      type: '员工指数'
    })),
    xField: 'month',
    yField: 'value',
    seriesField: 'type',
    yAxis: {
      label: {
        formatter: (v) => `${v}%`,
      },
    },
    tooltip: {
      formatter: (datum) => {
        return {
          name: datum.type,
          value: `${datum.value.toFixed(2)}%`
        };
      },
    },
    smooth: true,
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    );
  }

  const userMetrics = myMetrics?.user_metrics || {};
  const monthlyRankings = myMetrics?.monthly_rankings || [];

  return (
    <Layout style={{ padding: '24px' }}>
      <Content>
        <h1 style={{ marginBottom: 24 }}>
          <ThunderboltOutlined /> Agent 员工指数
        </h1>

        {/* 个人指标卡片 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="本月工作时长"
                value={userMetrics.total_hours || 0}
                suffix="小时"
                prefix={<ClockCircleOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="本月完成任务"
                value={userMetrics.total_tasks || 0}
                suffix="个"
                prefix={<ThunderboltOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="月度员工指数"
                value={formatEmployeeIndex(userMetrics.monthly_index || 0)}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
              <Progress
                percent={userMetrics.agent_load || 0}
                size="small"
                format={(percent) => `${percent}% Agent负荷`}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="月度排名"
                value={userMetrics.rank || '-'}
                prefix={getRankIcon(userMetrics.rank)}
                suffix={`/ ${monthlyRankings.length || 0}`}
              />
            </Card>
          </Col>
        </Row>

        {/* 标签页 */}
        <Card>
          <Tabs defaultActiveKey="rankings">
            <TabPane tab={<span><TrophyOutlined /> 排行榜</span>} key="rankings">
              <div style={{ marginBottom: 16 }}>
                <Radio.Group value={period} onChange={handlePeriodChange}>
                  <Radio.Button value="monthly">月度排行</Radio.Button>
                  <Radio.Button value="cumulative">累计排行</Radio.Button>
                </Radio.Group>
              </div>
              
              <Table
                columns={rankingColumns}
                dataSource={rankings}
                rowKey="user_id"
                pagination={false}
                rowClassName={(record) => 
                  record.user_id === userMetrics.user_id ? 'highlight-row' : ''
                }
              />
            </TabPane>

            <TabPane tab={<span><RiseOutlined /> 历史趋势</span>} key="history">
              {userHistory.length > 0 ? (
                <div>
                  <h3>近6个月员工指数趋势</h3>
                  <Line {...historyConfig} height={300} />
                  
                  <Table
                    style={{ marginTop: 24 }}
                    columns={[
                      { title: '月份', dataIndex: 'month', key: 'month' },
                      { title: '工作时长', dataIndex: 'hours', key: 'hours', render: h => `${h} 小时` },
                      { title: '任务数', dataIndex: 'task_count', key: 'task_count' },
                      { title: '员工指数', dataIndex: 'index', key: 'index', render: i => formatEmployeeIndex(i) },
                      { title: '排名', dataIndex: 'rank', key: 'rank' }
                    ]}
                    dataSource={userHistory}
                    rowKey="month"
                    pagination={false}
                  />
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: 50 }}>
                  暂无历史数据
                </div>
              )}
            </TabPane>

            {isAdmin && (
              <TabPane tab={<span><UserOutlined /> 公司统计</span>} key="company">
                <Button onClick={loadCompanyStats} type="primary" style={{ marginBottom: 16 }}>
                  加载公司统计
                </Button>
                
                {companyStats && (
                  <Row gutter={16}>
                    <Col span={12}>
                      <Card title="本月统计">
                        <Statistic title="活跃用户" value={companyStats.monthly_stats.total_users} />
                        <Statistic title="总工作时长" value={companyStats.monthly_stats.total_hours} suffix="小时" />
                        <Statistic title="平均工作时长" value={companyStats.monthly_stats.average_hours} suffix="小时/人" />
                        <Statistic title="平均Agent负荷" value={companyStats.monthly_stats.average_load} suffix="%" />
                      </Card>
                    </Col>
                    <Col span={12}>
                      <Card title="累计统计">
                        <Statistic title="总用户数" value={companyStats.cumulative_stats.total_users} />
                        <Statistic title="总工作时长" value={companyStats.cumulative_stats.total_hours} suffix="小时" />
                        <Statistic title="总任务数" value={companyStats.cumulative_stats.total_tasks} />
                        <Statistic title="平均工作时长" value={companyStats.cumulative_stats.average_hours} suffix="小时/人" />
                      </Card>
                    </Col>
                  </Row>
                )}
              </TabPane>
            )}
          </Tabs>
        </Card>
      </Content>
    </Layout>
  );
};

export default AgentIndexPage;