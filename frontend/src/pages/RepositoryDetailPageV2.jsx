import React, { useState, useEffect } from 'react';
import { Layout, Card, Button, Space, Tag, Empty, Spin, message, List, Badge, Row, Col, Statistic, Tooltip, Dropdown, Menu } from 'antd';
import {
  GithubOutlined,
  BranchesOutlined,
  ThunderboltOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  MoreOutlined,
  ArrowLeftOutlined,
  RocketOutlined,
  PlayCircleOutlined,
  EyeOutlined,
  PullRequestOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import { repositoryApi } from '../services/api';
import { useParams, useNavigate } from 'react-router-dom';
import QuickTaskButton from '../components/QuickTaskButton';
import axios from 'axios';

const { Content } = Layout;

const RepositoryDetailPageV2 = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [repository, setRepository] = useState(null);
  const [branches, setBranches] = useState([]);
  const [syncing, setSyncing] = useState(false);

  // 加载仓库详情和分支
  const loadRepository = async () => {
    setLoading(true);
    try {
      // 使用统一 API
      const [repoData, branchesData] = await Promise.all([
        repositoryApi.getRepository(id),
        axios.get(`/api/v2/repos/${id}/branches`)
      ]);
      
      setRepository(repoData);
      setBranches(branchesData.data.branches || []);
    } catch (error) {
      message.error('加载仓库详情失败');
      console.error('Load repository error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      loadRepository();
    }
  }, [id]);

  // 同步仓库
  const handleSyncRepository = async () => {
    setSyncing(true);
    try {
      await repositoryApi.syncRepository(id);
      message.success('仓库同步成功');
      loadRepository();
    } catch (error) {
      message.error('同步失败');
    } finally {
      setSyncing(false);
    }
  };

  // 快速执行分支
  const handleQuickExecute = async (branchId) => {
    try {
      await repositoryApi.executeBranch(branchId);
      message.success('任务执行中...');
      setTimeout(loadRepository, 2000);
    } catch (error) {
      message.error('执行失败');
    }
  };

  // 渲染分支状态
  const renderBranchStatus = (status) => {
    const statusMap = {
      draft: { color: 'default', text: '待执行', icon: null },
      in_progress: { color: 'processing', text: '执行中', icon: <LoadingOutlined spin /> },
      completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
      ready_for_review: { color: 'warning', text: '待审核', icon: null },
      merged: { color: 'success', text: '已合并', icon: <CheckCircleOutlined /> },
      failed: { color: 'error', text: '失败', icon: <CloseCircleOutlined /> }
    };
    
    const config = statusMap[status] || statusMap.draft;
    return (
      <Badge
        status={config.color}
        text={
          <Space size={4}>
            {config.icon}
            {config.text}
          </Space>
        }
      />
    );
  };

  // 分支操作菜单
  const getBranchMenu = (branch) => (
    <Menu>
      <Menu.Item key="execute" onClick={() => handleQuickExecute(branch.id)}>
        <PlayCircleOutlined /> 执行任务
      </Menu.Item>
      <Menu.Item key="view">
        <EyeOutlined /> 查看详情
      </Menu.Item>
      {branch.status === 'completed' && (
        <Menu.Item key="pr">
          <PullRequestOutlined /> 创建 PR
        </Menu.Item>
      )}
      <Menu.Divider />
      <Menu.Item key="delete" danger>
        <DeleteOutlined /> 删除分支
      </Menu.Item>
    </Menu>
  );

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!repository) {
    return (
      <Empty description="仓库不存在" style={{ marginTop: 100 }}>
        <Button onClick={() => navigate('/repositories')}>
          返回仓库列表
        </Button>
      </Empty>
    );
  }

  // 统计数据
  const stats = {
    total: branches.length,
    active: branches.filter(b => b.status === 'in_progress').length,
    completed: branches.filter(b => ['completed', 'merged'].includes(b.status)).length,
    failed: branches.filter(b => b.status === 'failed').length
  };

  return (
    <Layout style={{ padding: '24px', background: '#f0f2f5' }}>
      <Content>
        {/* 顶部操作栏 */}
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/repositories')}
          >
            返回
          </Button>
          <Space>
            <Button
              icon={<SyncOutlined />}
              loading={syncing}
              onClick={handleSyncRepository}
              disabled={!repository.github_url}
            >
              同步
            </Button>
            <QuickTaskButton
              repositoryId={id}
              onTaskCreated={loadRepository}
            />
          </Space>
        </div>

        {/* 仓库信息卡片 - 简化版 */}
        <Card style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space size="large">
              <GithubOutlined style={{ fontSize: 32 }} />
              <div>
                <h2 style={{ margin: 0 }}>
                  {repository.organization}/{repository.name}
                  {repository.is_private && (
                    <Tag color="orange" style={{ marginLeft: 8 }}>Private</Tag>
                  )}
                </h2>
                <p style={{ margin: '4px 0 0 0', color: '#666' }}>
                  {repository.description || '暂无描述'}
                </p>
              </div>
            </Space>
            
            {/* 快速统计 */}
            <Space size="large">
              <Statistic title="总任务" value={stats.total} />
              <Statistic 
                title="执行中" 
                value={stats.active} 
                valueStyle={{ color: '#1890ff' }}
              />
              <Statistic 
                title="已完成" 
                value={stats.completed} 
                valueStyle={{ color: '#52c41a' }}
              />
            </Space>
          </div>
        </Card>

        {/* 任务列表 - 简化版 */}
        <Card title={<span><RocketOutlined /> 任务列表</span>}>
          <List
            dataSource={branches}
            locale={{ emptyText: '暂无任务，点击"快速任务"创建第一个任务' }}
            renderItem={branch => {
              const isTask = branch.name.startsWith('task/');
              const taskTitle = isTask 
                ? branch.name.replace('task/', '').split('-').slice(1).join(' ')
                : branch.name;
              
              return (
                <List.Item
                  actions={[
                    branch.status === 'draft' ? (
                      <Tooltip title="执行任务">
                        <Button
                          type="primary"
                          size="small"
                          icon={<ThunderboltOutlined />}
                          onClick={() => handleQuickExecute(branch.id)}
                        >
                          执行
                        </Button>
                      </Tooltip>
                    ) : (
                      <Dropdown overlay={getBranchMenu(branch)} trigger={['click']}>
                        <Button size="small" icon={<MoreOutlined />} />
                      </Dropdown>
                    )
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <div style={{ 
                        width: 40, 
                        height: 40, 
                        borderRadius: 4,
                        background: isTask ? '#1890ff' : '#52c41a',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white'
                      }}>
                        {isTask ? <RocketOutlined /> : <BranchesOutlined />}
                      </div>
                    }
                    title={
                      <Space>
                        <span style={{ fontWeight: 500 }}>{taskTitle}</span>
                        {renderBranchStatus(branch.status)}
                      </Space>
                    }
                    description={
                      <div>
                        {branch.description && (
                          <p style={{ margin: '4px 0', color: '#666' }}>
                            {branch.description}
                          </p>
                        )}
                        <Space style={{ fontSize: 12, color: '#999' }}>
                          <span>{new Date(branch.created_at).toLocaleDateString()}</span>
                          {branch.execution_status && (
                            <>
                              <span>•</span>
                              <span>最后执行: {branch.execution_status}</span>
                            </>
                          )}
                        </Space>
                      </div>
                    }
                  />
                </List.Item>
              );
            }}
          />
        </Card>
      </Content>
    </Layout>
  );
};

export default RepositoryDetailPageV2;