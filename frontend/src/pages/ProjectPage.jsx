import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Row, Col, Card, Input, Button, Spin, Space, Modal, App, Tooltip } from 'antd'
import { SendOutlined, UploadOutlined, EditOutlined, SaveOutlined, CloseOutlined, FolderOutlined, BulbOutlined, DeleteOutlined } from '@ant-design/icons'
import FileExplorer from '../components/FileExplorer'
import CodeEditor from '../components/CodeEditor'
import TaskOutput from '../components/TaskOutput'
import FileUpload from '../components/FileUpload'
import TaskTemplates from '../components/TaskTemplates'
import PromptOptimizer from '../components/PromptOptimizer'
import TaskChainCreator from '../components/TaskChainCreator'
import LocalExecutionButton from '../components/LocalExecutionButton'
import { projectApi, taskApi } from '../services/api'
import { useSocketStore } from '../stores/socketStore'
import '../styles/ProjectPage.css'

const { TextArea } = Input

const ProjectPage = () => {
  const { message } = App.useApp()
  const navigate = useNavigate()
  const { projectName } = useParams()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [prompt, setPrompt] = useState('')
  const [executing, setExecuting] = useState(false)
  const [currentFile, setCurrentFile] = useState(null)
  const [currentTask, setCurrentTask] = useState(null)
  const [templateModalVisible, setTemplateModalVisible] = useState(false)
  const [editMode, setEditMode] = useState(false)
  const [editedContent, setEditedContent] = useState('')
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [optimizerVisible, setOptimizerVisible] = useState(false)
  
  const tasksRef = useRef(null)
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

  const handlePathUpdate = async () => {
    if (!newPath || newPath === (project.absolute_path || project.path)) {
      setEditingPath(false)
      return
    }
    
    try {
      const result = await projectApi.updateProject(projectName, newPath)
      message.success('项目路径更新成功')
      setEditingPath(false)
      
      // 如果项目名称变了，需要跳转到新的URL
      if (result.new_name !== projectName) {
        window.location.href = `/project/${result.new_name}`
      } else {
        loadProject()
      }
    } catch (error) {
      message.error('更新路径失败: ' + (error.response?.data?.error || error.message))
    }
  }

  const handleExecute = async () => {
    if (!prompt.trim()) {
      message.warning('Please enter a prompt')
      return
    }

    try {
      setExecuting(true)
      // 使用项目的绝对路径
      const projectPath = project.absolute_path || project.path
      console.log('Project data:', project)
      console.log('Using project path:', projectPath)
      
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
          // 跳转到任务一览页面
          navigate('/tasks')
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
        // 跳转到任务一览页面
        navigate('/tasks')
      }
    } catch (error) {
      console.error('Execute error:', error)
      const errorMsg = error.response?.data?.error || error.message || 'Failed to execute task'
      message.error(errorMsg)
      
      // 如果是路径错误，显示调试信息
      if (errorMsg.includes('path')) {
        console.log('Debug info:')
        console.log('Project name:', projectName)
        console.log('Project data:', project)
        console.log('Project path:', project?.path)
      }
    } finally {
      setExecuting(false)
    }
  }

  const handleFileSelect = async (file) => {
    if (file.type === 'file') {
      // 如果有未保存的更改，提示用户
      if (hasUnsavedChanges) {
        Modal.confirm({
          title: '未保存的更改',
          content: '当前文件有未保存的更改，是否放弃？',
          okText: '放弃更改',
          cancelText: '取消',
          onOk: async () => {
            await loadFile(file)
          }
        })
      } else {
        await loadFile(file)
      }
    }
  }
  
  const loadFile = async (file) => {
    try {
      const content = await projectApi.getFileContent(file.path)
      setCurrentFile({
        path: file.path,
        content: content.content,
        language: getLanguageFromPath(file.path)
      })
      setEditedContent(content.content)
      setEditMode(false)
      setHasUnsavedChanges(false)
    } catch (error) {
      message.error('Failed to load file')
    }
  }
  
  const handleSaveFile = async () => {
    if (!currentFile) return
    
    try {
      await projectApi.updateFileContent(currentFile.path, editedContent)
      message.success('文件保存成功')
      setCurrentFile({
        ...currentFile,
        content: editedContent
      })
      setHasUnsavedChanges(false)
      setEditMode(false)
    } catch (error) {
      message.error('保存文件失败: ' + (error.response?.data?.error || error.message))
    }
  }
  
  const handleContentChange = (value) => {
    setEditedContent(value)
    setHasUnsavedChanges(true)
  }

  const handleDeleteProject = async () => {
    Modal.confirm({
      title: '确认删除项目',
      content: `确定要删除项目 "${projectName}" 吗？此操作不可撤销。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await projectApi.deleteProject(projectName)
          message.success('项目删除成功')
          navigate('/') // 返回到项目列表
        } catch (error) {
          message.error('删除项目失败: ' + (error.response?.data?.error || error.message))
        }
      }
    })
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
    <div className="project-page-container">
      <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
        <div>
          <h1 style={{ marginBottom: 4, fontSize: '20px' }}>{projectName}</h1>
          {project && (
            <Space align="center" size="small">
              <FolderOutlined style={{ fontSize: '12px' }} />
              <Tooltip title="项目绝对路径">
                <span style={{ color: '#666', fontSize: '12px' }}>
                  {project.absolute_path || project.path}
                </span>
              </Tooltip>
            </Space>
          )}
        </div>
        <Button
          danger
          size="small"
          icon={<DeleteOutlined />}
          onClick={handleDeleteProject}
        >
          删除项目
        </Button>
      </div>
      
      <Row gutter={8} className="project-content-row">
        <Col xs={24} sm={24} md={5} lg={4} xl={4} className="project-col">
          <Card 
            title="文件" 
            size="small"
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
              onFileDeleted={() => loadProject()}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={24} md={14} lg={14} xl={14} className="project-col">
          <Card 
            title={currentFile ? `${editMode ? '编辑' : '查看'}: ${currentFile.path}${hasUnsavedChanges ? ' *' : ''}` : "Code Editor"} 
            size="small"
            style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
            bodyStyle={{ flex: 1, padding: 0, overflow: 'hidden' }}
            extra={currentFile && (
              <Space size="small">
                {editMode ? (
                  <>
                    <Button
                      type="primary"
                      size="small"
                      icon={<SaveOutlined />}
                      onClick={handleSaveFile}
                      disabled={!hasUnsavedChanges}
                    >
                      保存
                    </Button>
                    <Button
                      size="small"
                      icon={<CloseOutlined />}
                      onClick={() => {
                        if (hasUnsavedChanges) {
                          Modal.confirm({
                            title: '放弃更改？',
                            content: '是否放弃未保存的更改？',
                            okText: '放弃',
                            cancelText: '取消',
                            onOk: () => {
                              setEditedContent(currentFile.content)
                              setEditMode(false)
                              setHasUnsavedChanges(false)
                            }
                          })
                        } else {
                          setEditMode(false)
                        }
                      }}
                    >
                      取消
                    </Button>
                  </>
                ) : (
                  <Button
                    size="small"
                    icon={<EditOutlined />}
                    onClick={() => setEditMode(true)}
                  >
                    编辑
                  </Button>
                )}
              </Space>
            )}
          >
            {currentFile ? (
              <CodeEditor
                value={editMode ? editedContent : currentFile.content}
                onChange={editMode ? handleContentChange : undefined}
                language={currentFile.language}
                path={currentFile.path}
                readOnly={!editMode}
                options={{
                  fontSize: 14,
                  minimap: { enabled: false },
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  automaticLayout: true
                }}
              />
            ) : (
              <div style={{ 
                height: '100%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                color: '#999' 
              }}>
                选择一个文件查看内容
              </div>
            )}
          </Card>
        </Col>
        
        <Col xs={24} sm={24} md={5} lg={6} xl={6} className="project-col">
          <Card 
            title="Claude Code" 
            size="small"
            style={{ marginBottom: 8 }}
            extra={null}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
                <TaskChainCreator 
                  projectPath={project?.absolute_path || project?.path}
                  onChainCreated={(data) => {
                    if (data && data.parent_task_id) {
                      setCurrentTask({ 
                        id: data.parent_task_id, 
                        status: 'running', 
                        output: '任务链开始执行...\n',
                        task_type: 'parent',
                        prompt: data.task_chain?.prompt || '任务链',
                        project_path: data.task_chain?.project_path || projectPath
                      });
                      
                      if (tasksRef.current) {
                        tasksRef.current.refreshTasks();
                      }
                    } else {
                      console.error('Invalid task chain data:', data);
                    }
                  }}
                />
                <Button 
                  size="small"
                  onClick={() => setTemplateModalVisible(true)}
                >
                  模板
                </Button>
                <Tooltip title="优化提示词">
                  <Button 
                    size="small"
                    icon={<BulbOutlined />}
                    onClick={() => setOptimizerVisible(true)}
                    disabled={!prompt.trim()}
                  />
                </Tooltip>
                <LocalExecutionButton
                  prompt={prompt}
                  projectPath={project?.absolute_path || project?.path}
                  size="small"
                />
              </div>
              <TextArea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="在这里输入你的提示语..."
                rows={4}
                style={{ 
                  fontSize: '14px',
                  fontFamily: 'Consolas, Monaco, monospace'
                }}
                onPressEnter={(e) => {
                  if (e.ctrlKey || e.metaKey) {
                    handleExecute()
                  }
                }}
              />
              <Button 
                type="primary" 
                block
                icon={<SendOutlined />} 
                onClick={handleExecute}
                loading={executing}
              >
                执行 (Ctrl+Enter)
              </Button>
            </Space>
          </Card>
          
          <Card 
            title="输出" 
            size="small"
            style={{ flex: 1, overflow: 'hidden' }}
            bodyStyle={{ padding: 0, height: '100%' }}>
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

      <PromptOptimizer
        visible={optimizerVisible}
        onClose={() => setOptimizerVisible(false)}
        originalPrompt={prompt}
        onOptimize={(optimizedPrompt) => {
          setPrompt(optimizedPrompt)
        }}
      />
    </div>
  )
}

export default ProjectPage