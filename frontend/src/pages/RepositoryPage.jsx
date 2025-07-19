import React, { useState, useEffect } from 'react'
import { Layout, Card, Button, Space, Tag, Empty, Spin, Modal, Form, Input, Select, message, Row, Col, Statistic, Tooltip } from 'antd'
import {
  GithubOutlined,
  FolderOutlined,
  BranchesOutlined,
  IssuesCloseOutlined,
  PlusOutlined,
  SyncOutlined,
  LockOutlined,
  UnlockOutlined,
  StarOutlined,
  ForkOutlined,
  ImportOutlined
} from '@ant-design/icons'
import { repositoryApi } from '../services/api'
import { useNavigate } from 'react-router-dom'

const { Content } = Layout
const { TextArea } = Input
const { Option } = Select

const RepositoryPage = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [repositories, setRepositories] = useState([])
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [importModalVisible, setImportModalVisible] = useState(false)
  const [importLoading, setImportLoading] = useState(false)
  const [form] = Form.useForm()
  const [importForm] = Form.useForm()

  // 加载仓库列表
  const loadRepositories = async () => {
    setLoading(true)
    try {
      const data = await repositoryApi.listRepositories()
      setRepositories(data.repositories)
    } catch (error) {
      message.error('加载仓库列表失败')
      console.error('Load repositories error:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRepositories()
  }, [])

  // 创建仓库
  const handleCreateRepository = async (values) => {
    try {
      await repositoryApi.createRepository(values)
      message.success('仓库创建成功')
      setCreateModalVisible(false)
      form.resetFields()
      loadRepositories()
    } catch (error) {
      message.error('创建仓库失败')
      console.error('Create repository error:', error)
    }
  }

  // 导入 GitHub 仓库
  const handleImportRepository = async (values) => {
    setImportLoading(true)
    try {
      await repositoryApi.importRepository(values)
      message.success('仓库导入成功')
      setImportModalVisible(false)
      importForm.resetFields()
      loadRepositories()
    } catch (error) {
      message.error('导入仓库失败: ' + (error.response?.data?.error || error.message))
      console.error('Import repository error:', error)
    } finally {
      setImportLoading(false)
    }
  }

  // 渲染仓库卡片
  const renderRepositoryCard = (repo) => {
    const isPrivate = repo.is_private

    return (
      <Card
        key={repo.id}
        hoverable
        onClick={() => navigate(`/repository/${repo.id}`)}
        style={{ marginBottom: 12 }}
        actions={[
          <Tooltip title="分支">
            <Space>
              <BranchesOutlined />
              {repo.branch_count || 0}
            </Space>
          </Tooltip>,
          <Tooltip title="议题">
            <Space>
              <IssuesCloseOutlined />
              {repo.open_issue_count || 0}/{repo.issue_count || 0}
            </Space>
          </Tooltip>,
          <Tooltip title="同步状态">
            <SyncOutlined spin={false} />
          </Tooltip>
        ]}
      >
        <Card.Meta
          avatar={
            <div style={{ fontSize: 32, color: '#1890ff' }}>
              <FolderOutlined />
            </div>
          }
          title={
            <Space>
              <span>{repo.organization}/{repo.name}</span>
              {isPrivate ? (
                <Tag icon={<LockOutlined />} color="orange">Private</Tag>
              ) : (
                <Tag icon={<UnlockOutlined />} color="green">Public</Tag>
              )}
            </Space>
          }
          description={
            <div>
              <p>{repo.description || '暂无描述'}</p>
              {repo.github_url && (
                <Space style={{ marginTop: 8 }}>
                  <GithubOutlined />
                  <a href={repo.github_url} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}>
                    {repo.github_url}
                  </a>
                </Space>
              )}
            </div>
          }
        />
      </Card>
    )
  }

  return (
    <div>
        {/* 页面标题和操作 */}
        <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: 0 }}>
            <GithubOutlined style={{ marginRight: 8 }} />
            仓库管理
          </h1>
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              新建仓库
            </Button>
            <Button
              icon={<ImportOutlined />}
              onClick={() => setImportModalVisible(true)}
            >
              导入 GitHub 仓库
            </Button>
            <Button icon={<SyncOutlined />} onClick={loadRepositories}>
              刷新
            </Button>
          </Space>
        </div>

        {/* 统计信息 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总仓库数"
                value={repositories.length}
                prefix={<FolderOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总分支数"
                value={repositories.reduce((sum, repo) => sum + (repo.branch_count || 0), 0)}
                prefix={<BranchesOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="开放议题"
                value={repositories.reduce((sum, repo) => sum + (repo.open_issue_count || 0), 0)}
                prefix={<IssuesCloseOutlined />}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="已同步"
                value={repositories.filter(r => r.github_url).length}
                prefix={<GithubOutlined />}
                suffix={`/ ${repositories.length}`}
              />
            </Card>
          </Col>
        </Row>

        {/* 仓库列表 */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
          </div>
        ) : repositories.length > 0 ? (
          <div>
            {repositories.map(renderRepositoryCard)}
          </div>
        ) : (
          <Empty
            description="暂无仓库"
            style={{ marginTop: 50 }}
          >
            <Button type="primary" onClick={() => setCreateModalVisible(true)}>
              创建第一个仓库
            </Button>
          </Empty>
        )}

        {/* 创建仓库模态框 */}
        <Modal
          title="新建仓库"
          visible={createModalVisible}
          onCancel={() => {
            setCreateModalVisible(false)
            form.resetFields()
          }}
          footer={null}
          width={600}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleCreateRepository}
          >
            <Form.Item
              name="organization"
              label="组织"
              initialValue="personal"
            >
              <Select>
                <Option value="personal">个人仓库</Option>
                <Option value="sparticle">Sparticle</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="name"
              label="仓库名称"
              rules={[
                { required: true, message: '请输入仓库名称' },
                { pattern: /^[a-zA-Z0-9-_]+$/, message: '仓库名称只能包含字母、数字、横线和下划线' }
              ]}
            >
              <Input placeholder="my-awesome-project" />
            </Form.Item>

            <Form.Item
              name="description"
              label="描述"
            >
              <TextArea
                rows={3}
                placeholder="简要描述这个仓库的用途..."
              />
            </Form.Item>

            <Form.Item
              name="is_private"
              label="可见性"
              initialValue={false}
            >
              <Select>
                <Option value={false}>
                  <Space>
                    <UnlockOutlined />
                    Public - 所有人可见
                  </Space>
                </Option>
                <Option value={true}>
                  <Space>
                    <LockOutlined />
                    Private - 仅自己和协作者可见
                  </Space>
                </Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="github_url"
              label="GitHub 仓库地址（可选）"
              rules={[
                { type: 'url', message: '请输入有效的 URL' }
              ]}
            >
              <Input
                prefix={<GithubOutlined />}
                placeholder="https://github.com/username/repository"
              />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  创建仓库
                </Button>
                <Button onClick={() => {
                  setCreateModalVisible(false)
                  form.resetFields()
                }}>
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        {/* 导入仓库模态框 */}
        <Modal
          title="导入 GitHub 仓库"
          visible={importModalVisible}
          onCancel={() => {
            setImportModalVisible(false)
            importForm.resetFields()
          }}
          footer={null}
          width={600}
        >
          <Form
            form={importForm}
            layout="vertical"
            onFinish={handleImportRepository}
          >
            <Form.Item
              name="github_url"
              label="GitHub 仓库地址"
              rules={[
                { required: true, message: '请输入 GitHub 仓库地址' },
                { 
                  pattern: /^https:\/\/github\.com\/[\w-]+\/[\w.-]+$/,
                  message: '请输入有效的 GitHub 仓库地址，格式如: https://github.com/username/repository' 
                }
              ]}
            >
              <Input
                prefix={<GithubOutlined />}
                placeholder="https://github.com/username/repository"
              />
            </Form.Item>

            <div style={{ marginBottom: 16, padding: '12px', background: '#f0f2f5', borderRadius: 4 }}>
              <h4 style={{ marginTop: 0 }}>导入说明：</h4>
              <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                <li>仓库将被克隆到本地进行管理</li>
                <li>所有分支和议题信息将被同步</li>
                <li>如果是私有仓库，请确保已配置 GitHub 访问令牌</li>
                <li>导入后可以随时与 GitHub 同步</li>
              </ul>
            </div>

            <Form.Item>
              <Space>
                <Button 
                  type="primary" 
                  htmlType="submit"
                  loading={importLoading}
                  disabled={importLoading}
                >
                  开始导入
                </Button>
                <Button onClick={() => {
                  setImportModalVisible(false)
                  importForm.resetFields()
                }}>
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>
    </div>
  )
}

export default RepositoryPage