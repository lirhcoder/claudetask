import React, { useState, useEffect } from 'react'
import { Form, Input, Button, Card, message, Typography, Divider, Alert } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../services/api'

const { Title, Text, Link } = Typography

const LoginPage = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [isRegister, setIsRegister] = useState(false)
  const [emailDomain, setEmailDomain] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    // 获取系统配置
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const config = await authApi.getConfig()
      setEmailDomain(config.allowed_email_domain)
    } catch (error) {
      console.error('Failed to load config:', error)
    }
  }

  const handleSubmit = async (values) => {
    setLoading(true)
    try {
      if (isRegister) {
        await authApi.register(values)
        message.success('注册成功')
      } else {
        await authApi.login(values)
        message.success('登录成功')
      }
      
      // 跳转到首页
      navigate('/')
    } catch (error) {
      message.error(error.response?.data?.error || '操作失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: '#f0f2f5'
    }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>Claude Task Manager</Title>
          <Text type="secondary">{isRegister ? '创建新账户' : '登录您的账户'}</Text>
        </div>

        {emailDomain && isRegister && (
          <Alert
            message="注册要求"
            description={`只允许使用 ${emailDomain} 邮箱注册`}
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
              emailDomain && isRegister ? {
                validator: (_, value) => {
                  if (value && !value.endsWith(emailDomain)) {
                    return Promise.reject(`邮箱必须以 ${emailDomain} 结尾`)
                  }
                  return Promise.resolve()
                }
              } : null
            ].filter(Boolean)}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="邮箱地址"
              size="large"
            />
          </Form.Item>

          {isRegister && (
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' }
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名"
                size="large"
              />
            </Form.Item>
          )}

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              size="large"
            />
          </Form.Item>

          {isRegister && (
            <Form.Item
              name="confirmPassword"
              dependencies={['password']}
              rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve()
                    }
                    return Promise.reject('两次输入的密码不一致')
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="确认密码"
                size="large"
              />
            </Form.Item>
          )}

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
            >
              {isRegister ? '注册' : '登录'}
            </Button>
          </Form.Item>
        </Form>

        <Divider>或</Divider>

        <div style={{ textAlign: 'center' }}>
          <Text>
            {isRegister ? '已有账户？' : '还没有账户？'}
            <Link onClick={() => setIsRegister(!isRegister)} style={{ marginLeft: 8 }}>
              {isRegister ? '立即登录' : '立即注册'}
            </Link>
          </Text>
        </div>

        {!isRegister && (
          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              默认管理员账户：admin@claudetask.local / admin123
            </Text>
          </div>
        )}
      </Card>
    </div>
  )
}

export default LoginPage