import React, { useState, useEffect } from 'react'
import { Card, Form, Switch, InputNumber, Button, Space, message, Divider, Typography } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'

const { Title, Text } = Typography

const SettingsPage = () => {
  const [form] = Form.useForm()
  const [saving, setSaving] = useState(false)
  
  // 默认设置
  const defaultSettings = {
    autoRefresh: false,
    refreshInterval: 5,
    taskPageAutoRefresh: false,
    taskPageRefreshInterval: 5
  }

  useEffect(() => {
    // 从 localStorage 加载设置
    const savedSettings = localStorage.getItem('claudetask_settings')
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings)
        console.log('加载已保存的设置:', settings)
        form.setFieldsValue(settings)
      } catch (e) {
        console.error('加载设置失败:', e)
        form.setFieldsValue(defaultSettings)
      }
    } else {
      console.log('使用默认设置:', defaultSettings)
      form.setFieldsValue(defaultSettings)
    }
  }, [])

  const handleSave = async () => {
    try {
      setSaving(true)
      const values = await form.validateFields()
      
      // 保存到 localStorage
      localStorage.setItem('claudetask_settings', JSON.stringify(values))
      
      // 触发自定义事件，通知其他组件更新设置
      window.dispatchEvent(new CustomEvent('settings-updated', { detail: values }))
      
      message.success('设置已保存')
    } catch (error) {
      console.error('保存设置失败:', error)
      message.error('保存失败')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    form.setFieldsValue(defaultSettings)
    message.info('已重置为默认设置')
  }

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>系统设置</Title>
      
      <Card title="自动刷新设置" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            label="启用任务列表自动刷新"
            name="taskPageAutoRefresh"
            valuePropName="checked"
          >
            <Switch checkedChildren="开启" unCheckedChildren="关闭" />
          </Form.Item>

          <Form.Item
            label="任务列表刷新间隔（秒）"
            name="taskPageRefreshInterval"
            rules={[
              { required: true, message: '请输入刷新间隔' },
              { type: 'number', min: 2, max: 60, message: '间隔必须在2-60秒之间' }
            ]}
            dependencies={['taskPageAutoRefresh']}
          >
            <InputNumber
              min={2}
              max={60}
              style={{ width: 200 }}
              addonAfter="秒"
              disabled={!form.getFieldValue('taskPageAutoRefresh')}
            />
          </Form.Item>
          
          <Text type="secondary">
            控制任务页面列表的自动刷新频率。较短的间隔会更及时地显示任务状态更新，但可能增加服务器负载。
          </Text>
          
          <br />
          <br />
          
          <Text type="secondary">
            注：正在运行任务的持续时间会每秒自动更新，无需额外设置。
          </Text>


          <Form.Item style={{ marginTop: 32 }}>
            <Space>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                loading={saving}
                htmlType="submit"
              >
                保存设置
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
              >
                重置为默认
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card title="其他设置" style={{ marginBottom: 24 }}>
        <Text type="secondary">更多设置功能即将推出...</Text>
      </Card>
    </div>
  )
}

export default SettingsPage