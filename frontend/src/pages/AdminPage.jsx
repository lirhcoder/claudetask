import React, { useState, useEffect } from 'react'
import { Card, Table, Tabs, Form, Input, Button, message, Tag, Space, Statistic, Row, Col, Switch, Typography, Modal, Empty, Tooltip } from 'antd'
import { UserOutlined, ProjectOutlined, FileTextOutlined, SettingOutlined, ReloadOutlined, CrownOutlined, PlusOutlined, KeyOutlined, CopyOutlined } from '@ant-design/icons'
import { authApi, taskApi, projectApi } from '../services/api'

const { Title, Text } = Typography
const { TabPane } = Tabs

const AdminPage = () => {
  const [loading, setLoading] = useState(false)
  const [users, setUsers] = useState([])
  const [allTasks, setAllTasks] = useState([])
  const [allProjects, setAllProjects] = useState([])
  const [config, setConfig] = useState({})
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalTasks: 0,
    totalProjects: 0,
    runningTasks: 0
  })
  const [form] = Form.useForm()
  const [registerModalVisible, setRegisterModalVisible] = useState(false)
  const [registerForm] = Form.useForm()
  const [newUserPassword, setNewUserPassword] = useState('')
  const [tokenModalVisible, setTokenModalVisible] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [tokenForm] = Form.useForm()

  useEffect(() => {
    loadAllData()
  }, [])

  const loadAllData = async () => {
    setLoading(true)
    try {
      // 加载用户列表
      const usersData = await authApi.listUsers()
      setUsers(usersData.users)
      
      // 加载所有任务
      const tasksData = await taskApi.listAllTasks()
      setAllTasks(tasksData.tasks)
      
      // 加载所有项目
      const projectsData = await projectApi.listAllProjects()
      setAllProjects(projectsData.projects)
      
      // 加载系统配置
      const configData = await authApi.getAdminConfig()
      setConfig(configData)
      form.setFieldsValue({
        allowed_email_domain: configData.allowed_email_domain?.replace('@', '')
      })
      
      // 计算统计数据
      setStats({
        totalUsers: usersData.users.length,
        totalTasks: tasksData.tasks.length,
        totalProjects: projectsData.projects.length,
        runningTasks: tasksData.tasks.filter(t => t.status === 'running').length
      })
    } catch (error) {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  const handleConfigSave = async (values) => {
    try {
      await authApi.updateAdminConfig({
        allowed_email_domain: values.allowed_email_domain ? `@${values.allowed_email_domain}` : null
      })
      message.success('配置已更新')
      loadAllData()
    } catch (error) {
      message.error('更新配置失败')
    }
  }

  const handleMakeAdmin = async (userId) => {
    Modal.confirm({
      title: '确认操作',
      content: '确定要将此用户设置为管理员吗？',
      onOk: async () => {
        try {
          await authApi.makeUserAdmin(userId)
          message.success('已设置为管理员')
          loadAllData()
        } catch (error) {
          message.error('操作失败')
        }
      }
    })
  }

  const handleRegisterUser = async (values) => {
    try {
      const response = await authApi.adminRegisterUser(values)
      message.success('用户创建成功')
      setNewUserPassword(response.default_password)
      setRegisterModalVisible(false)
      registerForm.resetFields()
      loadAllData()
      
      // 显示默认密码
      Modal.info({
        title: '用户创建成功',
        content: (
          <div>
            <p>用户已创建成功，默认密码为：</p>
            <Input.Password 
              value={response.default_password} 
              readOnly 
              addonAfter={
                <Tooltip title="复制密码">
                  <CopyOutlined 
                    style={{ cursor: 'pointer' }}
                    onClick={() => {
                      navigator.clipboard.writeText(response.default_password)
                      message.success('密码已复制')
                    }}
                  />
                </Tooltip>
              }
            />
            <p style={{ marginTop: 16 }}>请通知用户首次登录后修改密码</p>
          </div>
        ),
        width: 480
      })
    } catch (error) {
      message.error('创建用户失败')
    }
  }

  const handleUpdateToken = async (values) => {
    try {
      await authApi.updateUserClaudeToken(selectedUser.id, values.claude_token)
      message.success('Claude token已更新')
      setTokenModalVisible(false)
      tokenForm.resetFields()
      loadAllData()
    } catch (error) {
      message.error('更新token失败')
    }
  }

  const userColumns = [
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      render: (email, record) => (
        <Space>
          {email}
          {record.is_admin && <Tag color="gold" icon={<CrownOutlined />}>管理员</Tag>}
        </Space>
      )
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username'
    },
    {
      title: 'Claude Token',
      dataIndex: 'claude_token',
      key: 'claude_token',
      width: 200,
      render: (token, record) => (
        <Space>
          {token ? (
            <Tooltip title={token}>
              <Text code>{token.substring(0, 8)}...</Text>
            </Tooltip>
          ) : (
            <Text type="secondary">未设置</Text>
          )}
          <Button
            size="small"
            icon={<KeyOutlined />}
            onClick={() => {
              setSelectedUser(record)
              tokenForm.setFieldsValue({ claude_token: record.claude_token || '' })
              setTokenModalVisible(true)
            }}
          >
            管理
          </Button>
        </Space>
      )
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString()
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      key: 'last_login',
      render: (date) => date ? new Date(date).toLocaleString() : '-'
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          {!record.is_admin && (
            <Button size="small" onClick={() => handleMakeAdmin(record.id)}>
              设为管理员
            </Button>
          )}
        </Space>
      )
    }
  ]

  const taskColumns = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      render: (id) => id.substring(0, 8) + '...'
    },
    {
      title: '用户',
      dataIndex: 'user_email',
      key: 'user_email',
      render: (email) => email || '未知用户'
    },
    {
      title: '提示词',
      dataIndex: 'prompt',
      key: 'prompt',
      ellipsis: true,
      width: 300
    },
    {
      title: '项目',
      dataIndex: 'project_path',
      key: 'project_path',
      render: (path) => path.split('/').pop()
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap = {
          pending: { color: 'default', text: 'Pending' },
          running: { color: 'processing', text: 'Running' },
          completed: { color: 'success', text: 'Completed' },
          failed: { color: 'error', text: 'Failed' },
          cancelled: { color: 'warning', text: 'Cancelled' }
        }
        const config = statusMap[status] || statusMap.pending
        return <Tag color={config.color}>{config.text}</Tag>
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString()
    }
  ]

  const projectColumns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '用户',
      dataIndex: 'user_email',
      key: 'user_email',
      render: (email) => email || '未知用户'
    },
    {
      title: '路径',
      dataIndex: 'path',
      key: 'path'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString()
    },
    {
      title: '任务数',
      dataIndex: 'task_count',
      key: 'task_count',
      render: (_, record) => {
        // 标准化路径以进行比较
        const normalizedProjectPath = record.path.replace(/\\/g, '/')
        const projectName = normalizedProjectPath.split('/').pop()
        
        // Debug: 打印第一次加载时的路径信息
        if (allTasks.length > 0 && !window._debuggedPaths) {
          window._debuggedPaths = true
          console.log('Project path:', record.path, '-> normalized:', normalizedProjectPath, '-> name:', projectName)
          console.log('Sample task paths:', allTasks.slice(0, 3).map(t => t.project_path))
        }
        
        const count = allTasks.filter(t => {
          if (!t.project_path) return false
          
          // 标准化任务路径
          const normalizedTaskPath = t.project_path.replace(/\\/g, '/')
          const taskProjectName = normalizedTaskPath.split('/').pop()
          
          // 比较完整路径或者项目名称
          return normalizedTaskPath === normalizedProjectPath || 
                 taskProjectName === projectName ||
                 normalizedTaskPath.endsWith('/' + projectName)
        }).length
        
        return count
      }
    }
  ]

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <CrownOutlined style={{ marginRight: 8 }} />
          超级管理员控制台
        </Title>
      </div>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总用户数"
              value={stats.totalUsers}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={stats.totalTasks}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总项目数"
              value={stats.totalProjects}
              prefix={<ProjectOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="运行中任务"
              value={stats.runningTasks}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Tabs defaultActiveKey="users">
          <TabPane tab={<span><UserOutlined />用户管理</span>} key="users">
            <Space style={{ marginBottom: 16 }}>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadAllData}
              >
                刷新数据
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setRegisterModalVisible(true)}
              >
                注册新用户
              </Button>
            </Space>
            <Table
              columns={userColumns}
              dataSource={users}
              rowKey="id"
              loading={loading}
            />
          </TabPane>

          <TabPane tab={<span><FileTextOutlined />所有任务</span>} key="tasks">
            <Table
              columns={taskColumns}
              dataSource={allTasks}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 20 }}
            />
          </TabPane>

          <TabPane tab={<span><ProjectOutlined />所有项目</span>} key="projects">
            <Table
              columns={projectColumns}
              dataSource={allProjects}
              rowKey="id"
              loading={loading}
            />
          </TabPane>

          <TabPane tab={<span><SettingOutlined />系统设置</span>} key="settings">
            <Card title="企业邮箱设置" style={{ maxWidth: 600 }}>
              <Form
                form={form}
                layout="vertical"
                onFinish={handleConfigSave}
              >
                <Form.Item
                  label="允许的邮箱域名"
                  name="allowed_email_domain"
                  help="留空表示允许任何邮箱注册。示例：company.com"
                >
                  <Input
                    addonBefore="@"
                    placeholder="company.com"
                  />
                </Form.Item>

                <Form.Item>
                  <Button type="primary" htmlType="submit">
                    保存设置
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </TabPane>
        </Tabs>
      </Card>

      {/* 注册新用户弹窗 */}
      <Modal
        title="注册新用户"
        open={registerModalVisible}
        onCancel={() => {
          setRegisterModalVisible(false)
          registerForm.resetFields()
        }}
        footer={null}
        width={600}
      >
        <Form
          form={registerForm}
          layout="vertical"
          onFinish={handleRegisterUser}
        >
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="user@company.com" />
          </Form.Item>

          <Form.Item
            name="username"
            label="用户名"
            help="留空则使用邮箱前缀作为用户名"
          >
            <Input placeholder="可选" />
          </Form.Item>

          <Form.Item
            name="claude_token"
            label="Claude Token"
            help="用于Claude登录的token，可以后续设置"
          >
            <Input.TextArea 
              placeholder="sk-ant-api03-..." 
              rows={3}
            />
          </Form.Item>

          <Form.Item
            name="is_admin"
            valuePropName="checked"
            initialValue={false}
          >
            <Switch checkedChildren="管理员" unCheckedChildren="普通用户" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                创建用户
              </Button>
              <Button onClick={() => {
                setRegisterModalVisible(false)
                registerForm.resetFields()
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 管理Claude Token弹窗 */}
      <Modal
        title="管理Claude Token"
        open={tokenModalVisible}
        onCancel={() => {
          setTokenModalVisible(false)
          tokenForm.resetFields()
          setSelectedUser(null)
        }}
        footer={null}
        width={600}
      >
        <Form
          form={tokenForm}
          layout="vertical"
          onFinish={handleUpdateToken}
        >
          <Form.Item label="用户">
            <Input value={selectedUser?.email} disabled />
          </Form.Item>

          <Form.Item
            name="claude_token"
            label="Claude Token"
            help="留空则清除token"
          >
            <Input.TextArea 
              placeholder="sk-ant-api03-..." 
              rows={3}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                更新Token
              </Button>
              <Button onClick={() => {
                setTokenModalVisible(false)
                tokenForm.resetFields()
                setSelectedUser(null)
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

export default AdminPage