import React, { useState, useEffect } from 'react'
import { Card, Form, Switch, InputNumber, Input, Select, Button, message, Typography, Tabs, Space, Modal, Tooltip, Tag, Divider, Alert } from 'antd'
import { 
  GithubOutlined, 
  KeyOutlined, 
  SettingOutlined, 
  ReloadOutlined,
  SaveOutlined,
  EyeInvisibleOutlined,
  EyeOutlined,
  InfoCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { configApi } from '../services/api'

const { Title, Text, Paragraph } = Typography
const { TabPane } = Tabs
const { Option } = Select
const { TextArea } = Input

const SettingsPage = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [configs, setConfigs] = useState({})
  const [showSecrets, setShowSecrets] = useState({})
  const [restartRequired, setRestartRequired] = useState(false)
  const [activeTab, setActiveTab] = useState('github')

  // 加载配置
  const loadConfigs = async () => {
    setLoading(true)
    try {
      const data = await configApi.getConfigs()
      setConfigs(data)
      
      // 将配置值设置到表单
      const formValues = {}
      Object.entries(data).forEach(([category, categoryConfigs]) => {
        Object.entries(categoryConfigs).forEach(([key, config]) => {
          formValues[key] = config.value
        })
      })
      form.setFieldsValue(formValues)
    } catch (error) {
      message.error('加载配置失败')
      console.error('Load configs error:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConfigs()
  }, [])

  // 保存配置
  const handleSave = async () => {
    try {
      setSaving(true)
      const values = form.getFieldsValue()
      
      // 只发送有变化的配置
      const changedConfigs = {}
      Object.entries(values).forEach(([key, value]) => {
        const originalValue = configs[key.split('.')[0]]?.[key]?.value
        if (value !== originalValue) {
          changedConfigs[key] = value
        }
      })

      if (Object.keys(changedConfigs).length === 0) {
        message.info('没有需要保存的更改')
        return
      }

      const response = await configApi.updateConfigs(changedConfigs)
      
      if (response.restart_required) {
        setRestartRequired(true)
        Modal.warning({
          title: '需要重启服务',
          content: '某些配置更改需要重启服务才能生效。',
          okText: '我知道了',
        })
      }

      message.success('配置保存成功')
      loadConfigs() // 重新加载配置
    } catch (error) {
      message.error('保存配置失败')
      console.error('Save configs error:', error)
    } finally {
      setSaving(false)
    }
  }

  // 重置配置
  const handleReset = () => {
    Modal.confirm({
      title: '确认重置',
      content: '是否确认重置所有配置为默认值？此操作不可恢复。',
      okText: '确认重置',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          await configApi.resetConfigs()
          message.success('配置已重置为默认值')
          loadConfigs()
        } catch (error) {
          message.error('重置配置失败')
          console.error('Reset configs error:', error)
        }
      }
    })
  }

  // 切换密码显示
  const toggleSecretVisibility = (key) => {
    setShowSecrets(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  // 渲染配置项
  const renderConfigItem = (key, config) => {
    const { value, type, description } = config
    
    // 敏感信息字段
    const isSensitive = ['access_token', 'webhook_secret', 'api_key'].some(s => key.includes(s))
    
    let inputComponent
    
    switch (type) {
      case 'boolean':
        inputComponent = (
          <Switch 
            checkedChildren="启用" 
            unCheckedChildren="禁用"
          />
        )
        break
        
      case 'integer':
        inputComponent = (
          <InputNumber 
            style={{ width: '100%' }}
            min={0}
          />
        )
        break
        
      case 'float':
        inputComponent = (
          <InputNumber 
            style={{ width: '100%' }}
            min={0}
            step={0.1}
          />
        )
        break
        
      case 'string':
        if (isSensitive) {
          inputComponent = (
            <Input.Password
              placeholder="输入密钥或令牌"
              iconRender={visible => (visible ? <EyeOutlined /> : <EyeInvisibleOutlined />)}
            />
          )
        } else if (key.includes('model') || key.includes('level') || key.includes('theme')) {
          // 下拉选择框
          const options = {
            'claude.model': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
            'task.log_level': ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            'ui.theme': ['light', 'dark'],
            'ui.language': ['zh-CN', 'en-US']
          }
          
          if (options[key]) {
            inputComponent = (
              <Select style={{ width: '100%' }}>
                {options[key].map(opt => (
                  <Option key={opt} value={opt}>{opt}</Option>
                ))}
              </Select>
            )
          } else {
            inputComponent = <Input />
          }
        } else {
          inputComponent = <Input />
        }
        break
        
      default:
        inputComponent = <Input />
    }
    
    return (
      <Form.Item
        key={key}
        name={key}
        label={
          <Space>
            <span>{description || key}</span>
            <Tooltip title={`配置键: ${key}`}>
              <InfoCircleOutlined style={{ color: '#999' }} />
            </Tooltip>
          </Space>
        }
        valuePropName={type === 'boolean' ? 'checked' : 'value'}
      >
        {inputComponent}
      </Form.Item>
    )
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>
          <SettingOutlined style={{ marginRight: 8 }} />
          系统设置
        </Title>
        <Space>
          <Button 
            icon={<ReloadOutlined />}
            onClick={loadConfigs}
            loading={loading}
          >
            刷新
          </Button>
          <Button 
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
          >
            保存更改
          </Button>
          <Button 
            danger
            onClick={handleReset}
          >
            重置为默认
          </Button>
        </Space>
      </div>

      {restartRequired && (
        <Alert
          message="需要重启服务"
          description="您修改的某些配置需要重启服务才能生效。"
          type="warning"
          showIcon
          icon={<ExclamationCircleOutlined />}
          style={{ marginBottom: 24 }}
          closable
        />
      )}

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane 
            tab={
              <span>
                <GithubOutlined />
                GitHub 集成
              </span>
            } 
            key="github"
          >
            <Card loading={loading}>
              <Title level={4}>GitHub 配置</Title>
              <Paragraph type="secondary">
                配置 GitHub 集成所需的访问令牌和 Webhook 设置
              </Paragraph>
              <Divider />
              
              {configs.github && Object.entries(configs.github).map(([key, config]) => 
                renderConfigItem(key, config)
              )}
              
              <Alert
                message="如何获取 GitHub Access Token?"
                description={
                  <div>
                    <p>1. 访问 GitHub Settings → Developer settings → Personal access tokens</p>
                    <p>2. 点击 "Generate new token"</p>
                    <p>3. 选择需要的权限（repo, workflow 等）</p>
                    <p>4. 生成并复制 token</p>
                  </div>
                }
                type="info"
                showIcon
                style={{ marginTop: 16 }}
              />
            </Card>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <KeyOutlined />
                Claude API
              </span>
            } 
            key="claude"
          >
            <Card loading={loading}>
              <Title level={4}>Claude 配置</Title>
              <Paragraph type="secondary">
                配置 Claude API 访问和模型参数
              </Paragraph>
              <Divider />
              
              {configs.claude && Object.entries(configs.claude).map(([key, config]) => 
                renderConfigItem(key, config)
              )}
              
              <Alert
                message="Claude API 说明"
                description={
                  <div>
                    <p>• API 密钥用于访问 Claude 服务</p>
                    <p>• 温度参数控制输出的随机性（0-1，越高越随机）</p>
                    <p>• 最大令牌数限制单次响应长度</p>
                  </div>
                }
                type="info"
                showIcon
                style={{ marginTop: 16 }}
              />
            </Card>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <SettingOutlined />
                任务执行
              </span>
            } 
            key="task"
          >
            <Card loading={loading}>
              <Title level={4}>任务配置</Title>
              <Paragraph type="secondary">
                配置任务执行的默认参数和行为
              </Paragraph>
              <Divider />
              
              {configs.task && Object.entries(configs.task).map(([key, config]) => 
                renderConfigItem(key, config)
              )}
            </Card>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <SettingOutlined />
                界面设置
              </span>
            } 
            key="ui"
          >
            <Card loading={loading}>
              <Title level={4}>界面配置</Title>
              <Paragraph type="secondary">
                自定义用户界面的显示和行为
              </Paragraph>
              <Divider />
              
              {configs.ui && Object.entries(configs.ui).map(([key, config]) => 
                renderConfigItem(key, config)
              )}
              
              <Alert
                message="界面设置说明"
                description="这些设置会保存在浏览器本地，并立即生效。"
                type="info"
                showIcon
                style={{ marginTop: 16 }}
              />
            </Card>
          </TabPane>

          <TabPane 
            tab={
              <span>
                <SettingOutlined />
                系统设置
              </span>
            } 
            key="system"
          >
            <Card loading={loading}>
              <Title level={4}>系统配置</Title>
              <Paragraph type="secondary">
                高级系统配置（需要管理员权限）
              </Paragraph>
              <Divider />
              
              {configs.system && Object.entries(configs.system).map(([key, config]) => 
                renderConfigItem(key, config)
              )}
              
              <Alert
                message="警告"
                description="修改系统配置可能影响服务稳定性，请谨慎操作。"
                type="warning"
                showIcon
                style={{ marginTop: 16 }}
              />
            </Card>
          </TabPane>
        </Tabs>
      </Form>
    </div>
  )
}

export default SettingsPage