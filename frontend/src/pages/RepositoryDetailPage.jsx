import React, { useState, useEffect } from 'react'
import { Layout, Card, Button, Space, Tag, Empty, Spin, Modal, Form, Input, Select, message, Tabs, List, Avatar, Badge, Breadcrumb, Row, Col, Statistic, Progress, Tooltip } from 'antd'
import {
  GithubOutlined,
  BranchesOutlined,
  IssuesCloseOutlined,
  PlusOutlined,
  SyncOutlined,
  PlayCircleOutlined,
  PullRequestOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  CodeOutlined,
  FileTextOutlined,
  TeamOutlined,
  CalendarOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons'
import { repositoryApi } from '../services/api'
import { useParams, useNavigate } from 'react-router-dom'

const { Content } = Layout
const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs

const RepositoryDetailPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [repository, setRepository] = useState(null)
  const [branches, setBranches] = useState([])
  const [issues, setIssues] = useState([])
  const [activeTab, setActiveTab] = useState('branches')
  const [createBranchModalVisible, setCreateBranchModalVisible] = useState(false)
  const [createIssueModalVisible, setCreateIssueModalVisible] = useState(false)
  const [selectedBranch, setSelectedBranch] = useState(null)
  const [executing, setExecuting] = useState({})
  const [syncing, setSyncing] = useState(false)
  const [branchForm] = Form.useForm()
  const [issueForm] = Form.useForm()

  // 加载仓库详情
  const loadRepository = async () => {
    setLoading(true)
    try {
      const data = await repositoryApi.getRepository(id)
      setRepository(data)
      setBranches(data.branches || [])
    } catch (error) {
      message.error('加载仓库详情失败')
      console.error('Load repository error:', error)
    } finally {
      setLoading(false)
    }
  }

  // 加载议题列表
  const loadIssues = async () => {
    try {
      const data = await repositoryApi.listIssues(id)
      setIssues(data.issues || [])
    } catch (error) {
      console.error('Load issues error:', error)
    }
  }

  useEffect(() => {
    if (id) {
      loadRepository()
      loadIssues()
    }
  }, [id])

  // 创建分支
  const handleCreateBranch = async (values) => {
    try {
      await repositoryApi.createBranch(id, values)
      message.success('分支创建成功')
      setCreateBranchModalVisible(false)
      branchForm.resetFields()
      loadRepository()
    } catch (error) {
      message.error('创建分支失败')
      console.error('Create branch error:', error)
    }
  }

  // 创建议题
  const handleCreateIssue = async (values) => {
    try {
      await repositoryApi.createIssue(id, values)
      message.success('议题创建成功')
      setCreateIssueModalVisible(false)
      issueForm.resetFields()
      loadIssues()
    } catch (error) {
      message.error('创建议题失败')
      console.error('Create issue error:', error)
    }
  }

  // 执行分支任务
  const handleExecuteBranch = async (branchId) => {
    setExecuting(prev => ({ ...prev, [branchId]: true }))
    try {
      await repositoryApi.executeBranch(branchId)
      message.success('任务已开始执行')
      // TODO: 通过 WebSocket 或轮询更新状态
      setTimeout(() => {
        loadRepository()
        setExecuting(prev => ({ ...prev, [branchId]: false }))
      }, 3000)
    } catch (error) {
      message.error('执行任务失败')
      console.error('Execute branch error:', error)
      setExecuting(prev => ({ ...prev, [branchId]: false }))
    }
  }

  // 同步仓库
  const handleSyncRepository = async () => {
    if (!repository.github_url) {
      message.warning('该仓库未关联 GitHub')
      return
    }
    
    setSyncing(true)
    try {
      const result = await repositoryApi.syncRepository(id)
      message.success('仓库同步成功')
      // 重新加载数据
      loadRepository()
      loadIssues()
    } catch (error) {
      message.error('同步失败: ' + (error.response?.data?.error || error.message))
      console.error('Sync repository error:', error)
    } finally {
      setSyncing(false)
    }
  }

  // 渲染分支状态图标
  const renderBranchStatus = (status) => {
    const statusConfig = {
      draft: { icon: <FileTextOutlined />, color: 'default', text: '草稿' },
      in_progress: { icon: <LoadingOutlined spin />, color: 'processing', text: '进行中' },
      review: { icon: <ClockCircleOutlined />, color: 'warning', text: '待审核' },
      merged: { icon: <CheckCircleOutlined />, color: 'success', text: '已合并' },
      closed: { icon: <CloseCircleOutlined />, color: 'error', text: '已关闭' }
    }
    const config = statusConfig[status] || statusConfig.draft
    return (
      <Tag icon={config.icon} color={config.color}>
        {config.text}
      </Tag>
    )
  }

  // 渲染议题优先级
  const renderPriority = (priority) => {
    const priorityConfig = {
      low: { color: 'default', text: '低' },
      medium: { color: 'blue', text: '中' },
      high: { color: 'orange', text: '高' },
      critical: { color: 'red', text: '紧急' }
    }
    const config = priorityConfig[priority] || priorityConfig.medium
    return <Tag color={config.color}>{config.text}</Tag>
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!repository) {
    return (
      <Empty
        description="仓库不存在"
        style={{ marginTop: 100 }}
      >
        <Button onClick={() => navigate('/repositories')}>
          返回仓库列表
        </Button>
      </Empty>
    )
  }

  return (
    <Layout style={{ padding: '24px' }}>
      <Content>
        {/* 面包屑导航 */}
        <Breadcrumb style={{ marginBottom: 16 }}>
          <Breadcrumb.Item>
            <a onClick={() => navigate('/repositories')}>仓库管理</a>
          </Breadcrumb.Item>
          <Breadcrumb.Item>{repository.organization}</Breadcrumb.Item>
          <Breadcrumb.Item>{repository.name}</Breadcrumb.Item>
        </Breadcrumb>

        {/* 仓库信息卡片 */}
        <Card style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ flex: 1 }}>
              <Space align="center" style={{ marginBottom: 16 }}>
                <h1 style={{ margin: 0 }}>
                  {repository.organization}/{repository.name}
                </h1>
                {repository.is_private ? (
                  <Tag color="orange">Private</Tag>
                ) : (
                  <Tag color="green">Public</Tag>
                )}
              </Space>
              <p style={{ color: '#666', marginBottom: 16 }}>
                {repository.description || '暂无描述'}
              </p>
              {repository.github_url && (
                <Space>
                  <GithubOutlined />
                  <a href={repository.github_url} target="_blank" rel="noopener noreferrer">
                    {repository.github_url}
                  </a>
                </Space>
              )}
            </div>
            <Space direction="vertical" align="end">
              <Button 
                icon={<SyncOutlined />} 
                loading={syncing}
                onClick={handleSyncRepository}
                disabled={!repository.github_url}
              >
                同步 GitHub
              </Button>
              <Button icon={<PullRequestOutlined />}>创建 PR</Button>
            </Space>
          </div>

          {/* 统计信息 */}
          <Row gutter={16} style={{ marginTop: 24 }}>
            <Col span={6}>
              <Statistic
                title="分支"
                value={branches.length}
                prefix={<BranchesOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="开放议题"
                value={issues.filter(i => i.status === 'open').length}
                prefix={<IssuesCloseOutlined />}
                suffix={`/ ${issues.length}`}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="贡献者"
                value={3}
                prefix={<TeamOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="最后更新"
                value={new Date(repository.updated_at).toLocaleDateString()}
                prefix={<CalendarOutlined />}
              />
            </Col>
          </Row>
        </Card>

        {/* 选项卡 */}
        <Card>
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane
              tab={
                <span>
                  <BranchesOutlined />
                  分支 ({branches.length})
                </span>
              }
              key="branches"
            >
              <div style={{ marginBottom: 16 }}>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setCreateBranchModalVisible(true)}
                >
                  新建分支
                </Button>
              </div>
              <List
                dataSource={branches}
                renderItem={branch => (
                  <List.Item
                    actions={[
                      <Button
                        type="primary"
                        size="small"
                        icon={<PlayCircleOutlined />}
                        loading={executing[branch.id]}
                        onClick={() => handleExecuteBranch(branch.id)}
                        disabled={branch.status === 'in_progress'}
                      >
                        执行
                      </Button>,
                      <Button size="small">查看</Button>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={<BranchesOutlined style={{ fontSize: 24 }} />}
                      title={
                        <Space>
                          <span>{branch.name}</span>
                          {renderBranchStatus(branch.status)}
                        </Space>
                      }
                      description={
                        <div>
                          <p>{branch.description}</p>
                          <Space style={{ fontSize: 12, color: '#999' }}>
                            <span>基于 {branch.base_branch}</span>
                            <span>•</span>
                            <span>创建于 {new Date(branch.created_at).toLocaleDateString()}</span>
                          </Space>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </TabPane>

            <TabPane
              tab={
                <span>
                  <IssuesCloseOutlined />
                  议题 ({issues.length})
                </span>
              }
              key="issues"
            >
              <div style={{ marginBottom: 16 }}>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setCreateIssueModalVisible(true)}
                >
                  新建议题
                </Button>
              </div>
              <List
                dataSource={issues}
                renderItem={issue => (
                  <List.Item
                    actions={[
                      <Button size="small">查看</Button>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar style={{ backgroundColor: issue.status === 'open' ? '#52c41a' : '#f5222d' }}>
                          #{issue.number}
                        </Avatar>
                      }
                      title={
                        <Space>
                          <span>{issue.title}</span>
                          {renderPriority(issue.priority)}
                          {issue.labels?.map(label => (
                            <Tag key={label.label} color={label.color}>
                              {label.label}
                            </Tag>
                          ))}
                        </Space>
                      }
                      description={
                        <div>
                          <p>{issue.description}</p>
                          <Space style={{ fontSize: 12, color: '#999' }}>
                            <span>由 {issue.created_by_email} 创建</span>
                            <span>•</span>
                            <span>{new Date(issue.created_at).toLocaleDateString()}</span>
                          </Space>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </TabPane>

            <TabPane
              tab={
                <span>
                  <CodeOutlined />
                  代码
                </span>
              }
              key="code"
            >
              <Empty description="代码浏览功能开发中" />
            </TabPane>
          </Tabs>
        </Card>

        {/* 创建分支模态框 */}
        <Modal
          title="新建分支"
          visible={createBranchModalVisible}
          onCancel={() => {
            setCreateBranchModalVisible(false)
            branchForm.resetFields()
          }}
          footer={null}
          width={600}
        >
          <Form
            form={branchForm}
            layout="vertical"
            onFinish={handleCreateBranch}
            initialValues={{ base_branch: 'main' }}
          >
            <Form.Item
              name="name"
              label="分支名称"
              rules={[
                { required: true, message: '请输入分支名称' },
                { pattern: /^[a-zA-Z0-9-_\/]+$/, message: '分支名称只能包含字母、数字、横线、下划线和斜线' }
              ]}
            >
              <Input
                placeholder="feature/add-login"
                prefix={<BranchesOutlined />}
              />
            </Form.Item>

            <Form.Item
              name="base_branch"
              label="基础分支"
            >
              <Select>
                <Option value="main">main</Option>
                {branches.map(branch => (
                  <Option key={branch.id} value={branch.name}>
                    {branch.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="description"
              label="任务描述"
              rules={[{ required: true, message: '请输入任务描述' }]}
            >
              <TextArea
                rows={4}
                placeholder="描述这个分支要完成的任务..."
              />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  创建分支
                </Button>
                <Button onClick={() => {
                  setCreateBranchModalVisible(false)
                  branchForm.resetFields()
                }}>
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        {/* 创建议题模态框 */}
        <Modal
          title="新建议题"
          visible={createIssueModalVisible}
          onCancel={() => {
            setCreateIssueModalVisible(false)
            issueForm.resetFields()
          }}
          footer={null}
          width={600}
        >
          <Form
            form={issueForm}
            layout="vertical"
            onFinish={handleCreateIssue}
            initialValues={{ priority: 'medium' }}
          >
            <Form.Item
              name="title"
              label="议题标题"
              rules={[{ required: true, message: '请输入议题标题' }]}
            >
              <Input placeholder="修复登录页面样式问题" />
            </Form.Item>

            <Form.Item
              name="description"
              label="议题描述"
            >
              <TextArea
                rows={4}
                placeholder="详细描述这个议题..."
              />
            </Form.Item>

            <Form.Item
              name="branch_id"
              label="关联分支（可选）"
            >
              <Select allowClear placeholder="选择关联的分支">
                {branches.map(branch => (
                  <Option key={branch.id} value={branch.id}>
                    {branch.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="priority"
              label="优先级"
            >
              <Select>
                <Option value="low">低</Option>
                <Option value="medium">中</Option>
                <Option value="high">高</Option>
                <Option value="critical">紧急</Option>
              </Select>
            </Form.Item>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  创建议题
                </Button>
                <Button onClick={() => {
                  setCreateIssueModalVisible(false)
                  issueForm.resetFields()
                }}>
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>
      </Content>
    </Layout>
  )
}

export default RepositoryDetailPage