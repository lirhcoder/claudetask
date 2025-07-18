import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Modal, Form, Input, message, Space, Tooltip, Typography, Tag, Spin, Empty, Switch } from 'antd'
import { FolderOutlined, PlusOutlined, DeleteOutlined, EditOutlined, EyeOutlined, ReloadOutlined, FolderOpenOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { projectApi } from '../services/api'
import PageLayout from '../components/PageLayout'

const { Title, Text } = Typography
const { confirm } = Modal

const ProjectsPage = () => {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [form] = Form.useForm()
  const navigate = useNavigate()

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const data = await projectApi.listProjects()
      setProjects(data.projects || [])
    } catch (error) {
      message.error('获取项目列表失败')
      console.error('Failed to fetch projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProject = async (values) => {
    try {
      await projectApi.createProject(values.name, values.initialize_readme)
      message.success('项目创建成功')
      setCreateModalVisible(false)
      form.resetFields()
      fetchProjects()
    } catch (error) {
      message.error('创建项目失败')
      console.error('Failed to create project:', error)
    }
  }

  const handleDeleteProject = (projectName) => {
    confirm({
      title: '确认删除',
      content: `确定要删除项目 "${projectName}" 吗？此操作不可恢复。`,
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          await projectApi.deleteProject(projectName)
          message.success('项目删除成功')
          fetchProjects()
        } catch (error) {
          message.error('删除项目失败')
          console.error('Failed to delete project:', error)
        }
      },
    })
  }

  const handleViewProject = (projectName) => {
    navigate(`/project/${projectName}`)
  }

  const columns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      render: (text) => (
        <Space>
          <FolderOpenOutlined style={{ color: '#1890ff' }} />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: '路径',
      dataIndex: 'path',
      key: 'path',
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <Text code>{text}</Text>
        </Tooltip>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => new Date(text).toLocaleString('zh-CN'),
      sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at),
    },
    {
      title: '最后修改',
      dataIndex: 'modified_at',
      key: 'modified_at',
      render: (text) => new Date(text).toLocaleString('zh-CN'),
      sorter: (a, b) => new Date(a.modified_at) - new Date(b.modified_at),
      defaultSortOrder: 'descend',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handleViewProject(record.name)}
            />
          </Tooltip>
          <Tooltip title="删除项目">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDeleteProject(record.name)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ]

  return (
    <PageLayout>
      <Card
        title={
          <Space>
            <FolderOutlined />
            <Title level={4} style={{ margin: 0 }}>项目管理</Title>
          </Space>
        }
        extra={
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchProjects}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              新建项目
            </Button>
          </Space>
        }
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
          </div>
        ) : projects.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="暂无项目"
            style={{ padding: '50px' }}
          >
            <Button type="primary" onClick={() => setCreateModalVisible(true)}>
              创建第一个项目
            </Button>
          </Empty>
        ) : (
          <Table
            columns={columns}
            dataSource={projects}
            rowKey="name"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个项目`,
            }}
          />
        )}
      </Card>

      <Modal
        title="新建项目"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false)
          form.resetFields()
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateProject}
          initialValues={{ initialize_readme: true }}
        >
          <Form.Item
            name="name"
            label="项目名称"
            rules={[
              { required: true, message: '请输入项目名称' },
              { pattern: /^[a-zA-Z0-9_-]+$/, message: '项目名称只能包含字母、数字、下划线和连字符' },
            ]}
          >
            <Input placeholder="my-project" />
          </Form.Item>
          <Form.Item
            name="initialize_readme"
            label="初始化 README"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                创建
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
    </PageLayout>
  )
}

export default ProjectsPage