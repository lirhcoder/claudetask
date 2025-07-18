import React, { useState } from 'react'
import { Layout, Card, Breadcrumb, Typography, Tabs, Button, Space, Empty, Spin, Tag, Divider } from 'antd'
import {
  HomeOutlined,
  FileTextOutlined,
  CodeOutlined,
  HistoryOutlined,
  FolderOpenOutlined,
  PlayCircleOutlined,
  EditOutlined
} from '@ant-design/icons'
import TaskFileExplorer from '../components/TaskFileExplorer'
import TaskOutput from '../components/TaskOutput'
import CodeEditor from '../components/CodeEditor'
import { taskApi, taskFileSystemApi } from '../services/api'
import { message } from 'antd'

const { Sider, Content } = Layout
const { Title, Text, Paragraph } = Typography
const { TabPane } = Tabs

const TaskWorkspace = () => {
  const [selectedTask, setSelectedTask] = useState(null)
  const [taskDetails, setTaskDetails] = useState(null)
  const [loading, setLoading] = useState(false)
  const [executing, setExecuting] = useState(false)
  const [siderCollapsed, setSiderCollapsed] = useState(false)

  // 处理任务选择
  const handleSelectTask = async (node) => {
    if (!node.isLeaf) return // 只处理任务节点，不处理文件夹
    
    setLoading(true)
    try {
      const response = await taskFileSystemApi.getTask(node.key)
      setSelectedTask(node)
      setTaskDetails(response)
    } catch (error) {
      console.error('Failed to load task details:', error)
      // 如果API失败，使用模拟数据
      const mockDetails = {
        id: node.key,
        name: node.title,
        path: node.key,
        prompt: '实现用户登录功能，包括表单验证和JWT认证',
        description: `# 用户登录功能实现

## 需求说明
实现一个完整的用户登录功能，包括前端表单和后端认证。

## 技术要求
- 前端使用React + Ant Design
- 后端使用Node.js + Express
- 使用JWT进行身份认证
- 密码需要加密存储

## 功能要求
1. 登录表单包含用户名和密码字段
2. 表单需要进行客户端验证
3. 登录成功后跳转到主页
4. 登录失败显示错误信息
5. 支持"记住我"功能

## 注意事项
- 考虑安全性，防止SQL注入和XSS攻击
- 合理的错误处理和用户提示
- 响应式设计，支持移动端`,
        status: node.status || 'pending',
        output: node.status === 'completed' ? '任务执行成功！\n已创建文件：\n- /src/components/LoginForm.jsx\n- /src/api/auth.js\n- /server/routes/auth.js' : null,
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T11:30:00Z',
        completed_at: node.status === 'completed' ? '2024-01-15T11:30:00Z' : null,
        resources: [
          { name: 'LoginForm.jsx', type: 'code', language: 'javascript' },
          { name: 'auth.js', type: 'code', language: 'javascript' },
          { name: 'auth.test.js', type: 'test', language: 'javascript' }
        ]
      }
      
      setSelectedTask(node)
      setTaskDetails(mockDetails)
    } finally {
      setLoading(false)
    }
  }

  // 处理执行任务
  const handleExecuteTask = async (task) => {
    setExecuting(true)
    try {
      const result = await taskFileSystemApi.executeTask(task.key || selectedTask?.key)
      message.success('任务已提交执行')
      // TODO: 轮询或websocket获取执行状态
      setTimeout(() => {
        handleSelectTask(task || selectedTask) // 刷新任务详情
      }, 2000)
    } catch (error) {
      message.error('执行任务失败')
      console.error('Execute error:', error)
    } finally {
      setExecuting(false)
    }
  }

  // 渲染面包屑
  const renderBreadcrumb = () => {
    if (!selectedTask) return null
    
    const paths = selectedTask.key.split('/').filter(p => p)
    return (
      <Breadcrumb>
        <Breadcrumb.Item href="/">
          <HomeOutlined />
        </Breadcrumb.Item>
        {paths.map((path, index) => (
          <Breadcrumb.Item key={index}>
            {index === paths.length - 1 ? (
              <span>{path}</span>
            ) : (
              <a href={`#${paths.slice(0, index + 1).join('/')}`}>{path}</a>
            )}
          </Breadcrumb.Item>
        ))}
      </Breadcrumb>
    )
  }

  // 渲染任务状态标签
  const renderStatusTag = (status) => {
    const statusMap = {
      pending: { color: 'default', text: '待执行' },
      running: { color: 'processing', text: '执行中' },
      completed: { color: 'success', text: '已完成' },
      failed: { color: 'error', text: '执行失败' }
    }
    const config = statusMap[status] || { color: 'default', text: status }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 左侧文件浏览器 */}
      <Sider
        width={300}
        collapsible
        collapsed={siderCollapsed}
        onCollapse={setSiderCollapsed}
        style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}
      >
        <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
          <Title level={5} style={{ margin: 0 }}>
            <FolderOpenOutlined /> 任务资源管理器
          </Title>
        </div>
        <TaskFileExplorer
          onSelectTask={handleSelectTask}
          onExecuteTask={handleExecuteTask}
        />
      </Sider>

      {/* 右侧内容区 */}
      <Content style={{ background: '#f0f2f5', overflow: 'auto' }}>
        {selectedTask ? (
          <div style={{ padding: '16px' }}>
            {/* 面包屑导航 */}
            {renderBreadcrumb()}
            
            {/* 任务详情卡片 */}
            <Card
              style={{ marginTop: 16 }}
              loading={loading}
              title={
                <Space>
                  <FileTextOutlined />
                  <span>{taskDetails?.name}</span>
                  {taskDetails && renderStatusTag(taskDetails.status)}
                </Space>
              }
              extra={
                <Space>
                  <Button icon={<EditOutlined />}>编辑</Button>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={() => handleExecuteTask(selectedTask)}
                    loading={executing}
                    disabled={taskDetails?.status === 'running'}
                  >
                    执行任务
                  </Button>
                </Space>
              }
            >
              <Tabs defaultActiveKey="readme">
                <TabPane tab="任务说明 (README)" key="readme">
                  <div style={{ maxWidth: 800 }}>
                    <Title level={5}>任务描述</Title>
                    <Paragraph>
                      <Text strong>{taskDetails?.prompt}</Text>
                    </Paragraph>
                    
                    <Divider />
                    
                    <div style={{ whiteSpace: 'pre-wrap' }}>
                      {taskDetails?.description || '暂无详细说明'}
                    </div>
                  </div>
                </TabPane>
                
                <TabPane tab="执行结果" key="output">
                  {taskDetails?.output ? (
                    <TaskOutput output={taskDetails.output} />
                  ) : (
                    <Empty description="暂无执行结果" />
                  )}
                </TabPane>
                
                <TabPane tab="生成的代码" key="code">
                  {taskDetails?.resources?.filter(r => r.type === 'code').length > 0 ? (
                    <Tabs tabPosition="left">
                      {taskDetails.resources
                        .filter(r => r.type === 'code')
                        .map(resource => (
                          <TabPane tab={resource.name} key={resource.name}>
                            <CodeEditor
                              value={`// ${resource.name}\n// TODO: Load actual code content`}
                              language={resource.language}
                              readOnly
                            />
                          </TabPane>
                        ))}
                    </Tabs>
                  ) : (
                    <Empty description="暂无生成的代码" />
                  )}
                </TabPane>
                
                <TabPane tab="执行历史" key="history">
                  <Empty description="暂无执行历史" />
                </TabPane>
              </Tabs>
            </Card>
          </div>
        ) : (
          <div style={{ 
            height: '100%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center' 
          }}>
            <Empty
              description="请从左侧选择一个任务"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          </div>
        )}
      </Content>
    </Layout>
  )
}

export default TaskWorkspace