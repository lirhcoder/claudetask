import React, { useState, useEffect } from 'react'
import { Card, Form, Switch, InputNumber, message, Typography } from 'antd'

const { Title, Text } = Typography

const SettingsPage = () => {
  const [form] = Form.useForm()
  
  // 默认设置
  const defaultSettings = {
    autoRefresh: false,
    refreshInterval: 5,
    taskPageAutoRefresh: false,
    taskPageRefreshInterval: 5
  }

  // 加载设置
  useEffect(() => {
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

  // 保存设置的通用函数
  const saveSettings = (changedValues, allValues) => {
    try {
      // 保存到 localStorage
      localStorage.setItem('claudetask_settings', JSON.stringify(allValues))
      
      // 触发自定义事件，通知其他组件更新设置
      window.dispatchEvent(new CustomEvent('settings-updated', { detail: allValues }))
      
      console.log('设置已自动保存:', allValues)
    } catch (error) {
      console.error('保存设置失败:', error)
      message.error('保存设置失败')
    }
  }

  // 处理开关变化
  const handleSwitchChange = (checked) => {
    const allValues = form.getFieldsValue()
    allValues.taskPageAutoRefresh = checked
    form.setFieldsValue(allValues)
    saveSettings({ taskPageAutoRefresh: checked }, allValues)
  }

  // 处理间隔时间变化
  const handleIntervalChange = (value) => {
    // 验证值的有效性
    if (value && value >= 2 && value <= 60) {
      const allValues = form.getFieldsValue()
      allValues.taskPageRefreshInterval = value
      form.setFieldsValue(allValues)
      saveSettings({ taskPageRefreshInterval: value }, allValues)
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>系统设置</Title>
      
      <Card title="自动刷新设置" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            label="启用任务列表自动刷新"
            name="taskPageAutoRefresh"
            valuePropName="checked"
          >
            <Switch 
              checkedChildren="开启" 
              unCheckedChildren="关闭"
              onChange={handleSwitchChange}
            />
          </Form.Item>

          <Form.Item
            label="任务列表刷新间隔（秒）"
            name="taskPageRefreshInterval"
            rules={[
              { required: true, message: '请输入刷新间隔' },
              { type: 'number', min: 2, max: 60, message: '间隔必须在2-60秒之间' }
            ]}
          >
            <InputNumber
              min={2}
              max={60}
              style={{ width: 200 }}
              addonAfter="秒"
              onBlur={(e) => {
                const value = parseInt(e.target.value)
                if (!isNaN(value)) {
                  handleIntervalChange(value)
                }
              }}
              onPressEnter={(e) => {
                const value = parseInt(e.target.value)
                if (!isNaN(value)) {
                  handleIntervalChange(value)
                }
              }}
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
          
          <br />
          <br />
          
          <Text type="secondary" style={{ fontStyle: 'italic' }}>
            提示：所有设置会自动保存，无需手动点击保存按钮。
          </Text>
        </Form>
      </Card>

      <Card title="其他设置" style={{ marginBottom: 24 }}>
        <Text type="secondary">更多设置功能即将推出...</Text>
      </Card>
    </div>
  )
}

export default SettingsPage