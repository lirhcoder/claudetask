import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Row, Col, Card, Input, Button, message, Spin, Space, Modal } from 'antd'
import { SendOutlined, UploadOutlined } from '@ant-design/icons'
import FileExplorer from '../components/FileExplorer'
import CodeEditor from '../components/CodeEditor'
import TaskOutput from '../components/TaskOutput'
import FileUpload from '../components/FileUpload'
import TaskTemplates from '../components/TaskTemplates'
import { projectApi, taskApi } from '../services/api'
import { useSocketStore } from '../stores/socketStore'

const { TextArea } = Input

const ProjectPage = () => {
  const { projectName } = useParams()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [prompt, setPrompt] = useState('')
  const [executing, setExecuting] = useState(false)
  const [currentFile, setCurrentFile] = useState(null)
  const [currentTask, setCurrentTask] = useState(null)
  const [templateModalVisible, setTemplateModalVisible] = useState(false)
  
  const { socket, connectSocket } = useSocketStore()

  useEffect(() => {
    loadProject()
    // 只在需要时连接 Socket
    const enableSocket = import.meta.env.VITE_ENABLE_SOCKET !== 'false'
    if (enableSocket && !socket) {
      try {
        connectSocket()
      } catch (error) {
        console.log('Socket connection failed, running in offline mode')
      }
    }
  }, [projectName])

  useEffect(() => {
    if (socket && currentTask) {
      socket.emit('subscribe_task', { task_id: currentTask.id })
      
      return () => {
        socket.emit('unsubscribe_task', { task_id: currentTask.id })
      }
    }
  }, [socket, currentTask])

  const loadProject = async () => {
    try {
      setLoading(true)
      const data = await projectApi.getProjectDetails(projectName)
      setProject(data)
    } catch (error) {
      message.error('Failed to load project')
    } finally {
      setLoading(false)
    }
  }

  const handleExecute = async () => {
    if (!prompt.trim()) {
      message.warning('Please enter a prompt')
      return
    }

    try {
      setExecuting(true)
      const projectPath = project.path
      
      if (socket) {
        // Use WebSocket for real-time updates
        socket.emit('execute_code', {
          prompt: prompt.trim(),
          project_path: projectPath
        })
        
        socket.once('execution_started', (data) => {
          setCurrentTask({ id: data.task_id, status: 'running', output: '' })
          message.success('Task started')
          setPrompt('')
        })
        
        socket.once('execution_error', (data) => {
          message.error(data.error)
          setExecuting(false)
        })
      } else {
        // Fallback to REST API
        const response = await taskApi.executeTask(prompt.trim(), projectPath)
        setCurrentTask({ id: response.task_id, status: 'queued', output: '' })
        message.success('Task queued')
        setPrompt('')
      }
    } catch (error) {
      message.error('Failed to execute task')
    } finally {
      setExecuting(false)
    }
  }

  const handleFileSelect = async (file) => {
    if (file.type === 'file') {
      try {
        const content = await projectApi.getFileContent(`${projectName}/${file.path}`)
        setCurrentFile({
          path: file.path,
          content: content.content,
          language: getLanguageFromPath(file.path)
        })
      } catch (error) {
        message.error('Failed to load file')
      }
    }
  }

  const getLanguageFromPath = (path) => {
    const ext = path.split('.').pop()
    const languageMap = {
      js: 'javascript',
      jsx: 'javascript',
      ts: 'typescript',
      tsx: 'typescript',
      py: 'python',
      java: 'java',
      cpp: 'cpp',
      c: 'c',
      cs: 'csharp',
      php: 'php',
      rb: 'ruby',
      go: 'go',
      rs: 'rust',
      kt: 'kotlin',
      swift: 'swift',
      m: 'objective-c',
      scala: 'scala',
      sh: 'shell',
      sql: 'sql',
      html: 'html',
      xml: 'xml',
      css: 'css',
      scss: 'scss',
      sass: 'sass',
      less: 'less',
      json: 'json',
      md: 'markdown',
      yaml: 'yaml',
      yml: 'yaml'
    }
    return languageMap[ext] || 'plaintext'
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div style={{ height: 'calc(100vh - 160px)' }}>
      <h1 style={{ marginBottom: 16 }}>{projectName}</h1>
      
      <Row gutter={16} style={{ height: '100%' }}>
        <Col span={6} style={{ height: '100%' }}>
          <Card 
            title="Files" 
            style={{ height: '100%', overflow: 'auto' }}
            extra={
              <FileUpload 
                projectName={projectName}
                onUploadSuccess={() => loadProject()}
                mode="button"
              />
            }
          >
            <FileExplorer 
              files={project?.files || []} 
              onFileSelect={handleFileSelect}
            />
          </Card>
        </Col>
        
        <Col span={12} style={{ height: '100%' }}>
          <Card title="Code Editor" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              {currentFile ? (
                <CodeEditor
                  value={currentFile.content}
                  language={currentFile.language}
                  path={currentFile.path}
                  readOnly
                />
              ) : (
                <div style={{ padding: 20, textAlign: 'center', color: '#999' }}>
                  Select a file to view
                </div>
              )}
            </div>
          </Card>
        </Col>
        
        <Col span={6} style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Card 
            title="Claude Code" 
            style={{ marginBottom: 16 }}
            extra={
              <Space>
                <Button 
                  onClick={() => setTemplateModalVisible(true)}
                >
                  模板
                </Button>
                <Button 
                  type="primary" 
                  icon={<SendOutlined />} 
                  onClick={handleExecute}
                  loading={executing}
                >
                  Execute
                </Button>
              </Space>
            }
          >
            <TextArea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your prompt here..."
              rows={4}
              onPressEnter={(e) => {
                if (e.ctrlKey || e.metaKey) {
                  handleExecute()
                }
              }}
            />
          </Card>
          
          <Card title="Output" style={{ flex: 1, overflow: 'hidden' }}>
            {currentTask && (
              <TaskOutput task={currentTask} />
            )}
          </Card>
        </Col>
      </Row>

      <Modal
        title="任务模板"
        open={templateModalVisible}
        onCancel={() => setTemplateModalVisible(false)}
        footer={null}
        width={800}
      >
        <TaskTemplates 
          onUseTemplate={(template) => {
            setPrompt(template)
            setTemplateModalVisible(false)
          }}
        />
      </Modal>
    </div>
  )
}

export default ProjectPage