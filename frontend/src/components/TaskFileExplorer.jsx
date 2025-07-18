import React, { useState, useEffect } from 'react'
import { Tree, Input, Button, Dropdown, Menu, Modal, Form, Space, message, Tooltip } from 'antd'
import {
  FolderOutlined,
  FolderOpenOutlined,
  FileTextOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  ReloadOutlined,
  FileAddOutlined,
  FolderAddOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'
import { taskFileSystemApi } from '../services/api'

const { DirectoryTree } = Tree
const { Search } = Input
const { TextArea } = Input

const TaskFileExplorer = ({ onSelectTask, onExecuteTask }) => {
  const [treeData, setTreeData] = useState([])
  const [expandedKeys, setExpandedKeys] = useState([])
  const [selectedKeys, setSelectedKeys] = useState([])
  const [searchValue, setSearchValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [createType, setCreateType] = useState('folder') // 'folder' or 'task'
  const [selectedNode, setSelectedNode] = useState(null)
  const [form] = Form.useForm()

  // 转换任务树数据格式
  const convertToTreeData = (node) => {
    const treeNode = {
      title: node.name,
      key: node.path,
      icon: node.is_folder ? <FolderOutlined /> : <FileTextOutlined />,
      isLeaf: !node.is_folder,
      status: node.status,
      children: []
    }
    
    if (node.children && node.children.length > 0) {
      treeNode.children = node.children.map(child => convertToTreeData(child))
    }
    
    return treeNode
  }

  // 加载任务树
  const loadTaskTree = async () => {
    setLoading(true)
    try {
      const response = await taskFileSystemApi.getTaskTree('/', 3)
      
      if (response.children && response.children.length > 0) {
        const treeData = response.children.map(child => convertToTreeData(child))
        setTreeData(treeData)
        
        // 默认展开第一个项目
        if (treeData.length > 0) {
          setExpandedKeys([treeData[0].key])
        }
      } else {
        setTreeData([])
      }
    } catch (error) {
      console.error('Failed to load task tree:', error)
      // 如果API失败，使用模拟数据
      const mockData = [
        {
          title: 'Project Alpha',
          key: '/project-alpha',
          icon: <FolderOutlined />,
          children: [
            {
              title: 'Feature 1',
              key: '/project-alpha/feature-1',
              icon: <FolderOutlined />,
              children: [
                {
                  title: 'Implement Login',
                  key: '/project-alpha/feature-1/implement-login',
                  icon: <FileTextOutlined />,
                  status: 'completed',
                  isLeaf: true
                },
                {
                  title: 'Add Authentication',
                  key: '/project-alpha/feature-1/add-auth',
                  icon: <FileTextOutlined />,
                  status: 'running',
                  isLeaf: true
                }
              ]
            },
            {
              title: 'Bug Fixes',
              key: '/project-alpha/bug-fixes',
              icon: <FolderOutlined />,
              children: [
                {
                  title: 'Fix Memory Leak',
                  key: '/project-alpha/bug-fixes/fix-memory',
                  icon: <FileTextOutlined />,
                  status: 'failed',
                  isLeaf: true
                }
              ]
            }
          ]
        },
        {
          title: 'Project Beta',
          key: '/project-beta',
          icon: <FolderOutlined />,
          children: [
            {
              title: 'Database Migration',
              key: '/project-beta/db-migration',
              icon: <FileTextOutlined />,
              status: 'pending',
              isLeaf: true
            }
          ]
        }
      ]
      
      setTreeData(mockData)
      setExpandedKeys(['/project-alpha']) // 默认展开第一个项目
      }
    } catch (error) {
      message.error('加载任务树失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTaskTree()
  }, [])

  // 获取任务状态图标
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />
      case 'running':
        return <LoadingOutlined style={{ color: '#1890ff' }} spin />
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'failed':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
      default:
        return null
    }
  }

  // 渲染树节点标题
  const renderTitle = (node) => {
    const statusIcon = node.status ? getStatusIcon(node.status) : null
    
    return (
      <Space>
        {node.title}
        {statusIcon}
      </Space>
    )
  }

  // 树节点右键菜单
  const getNodeMenu = (node) => (
    <Menu>
      {!node.isLeaf && (
        <>
          <Menu.Item 
            key="new-folder" 
            icon={<FolderAddOutlined />}
            onClick={() => handleCreate('folder', node)}
          >
            新建子文件夹
          </Menu.Item>
          <Menu.Item 
            key="new-task" 
            icon={<FileAddOutlined />}
            onClick={() => handleCreate('task', node)}
          >
            新建子任务
          </Menu.Item>
          <Menu.Divider />
        </>
      )}
      {node.isLeaf && (
        <>
          <Menu.Item 
            key="execute" 
            icon={<PlayCircleOutlined />}
            onClick={() => handleExecute(node)}
          >
            执行任务
          </Menu.Item>
          <Menu.Divider />
        </>
      )}
      <Menu.Item 
        key="rename" 
        icon={<EditOutlined />}
        onClick={() => handleRename(node)}
      >
        重命名
      </Menu.Item>
      <Menu.Item 
        key="delete" 
        icon={<DeleteOutlined />} 
        danger
        onClick={() => handleDelete(node)}
      >
        删除
      </Menu.Item>
    </Menu>
  )

  // 处理创建
  const handleCreate = (type, parentNode) => {
    setCreateType(type)
    setSelectedNode(parentNode)
    setCreateModalVisible(true)
  }

  // 处理创建提交
  const handleCreateSubmit = async (values) => {
    try {
      const data = {
        parent_path: selectedNode?.key || '/',
        name: values.name,
        type: createType,
        prompt: values.prompt || '',
        description: values.readme || ''
      }
      
      await taskFileSystemApi.createTask(data)
      message.success(`${createType === 'folder' ? '文件夹' : '任务'}创建成功`)
      setCreateModalVisible(false)
      form.resetFields()
      loadTaskTree()
    } catch (error) {
      message.error('创建失败')
      console.error('Create error:', error)
    }
  }

  // 处理执行任务
  const handleExecute = (node) => {
    if (onExecuteTask) {
      onExecuteTask(node)
    }
  }

  // 处理重命名
  const handleRename = (node) => {
    // TODO: 实现重命名功能
    console.log('Rename:', node)
  }

  // 处理删除
  const handleDelete = (node) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除 "${node.title}" 吗？`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          // TODO: 调用API删除
          message.success('删除成功')
          loadTaskTree()
        } catch (error) {
          message.error('删除失败')
        }
      }
    })
  }

  // 处理选择
  const handleSelect = (selectedKeys, { node }) => {
    setSelectedKeys(selectedKeys)
    if (onSelectTask && node.isLeaf) {
      onSelectTask(node)
    }
  }

  // 处理搜索
  const handleSearch = (value) => {
    setSearchValue(value)
    // TODO: 实现搜索过滤
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 工具栏 */}
      <div style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>
        <Space>
          <Search
            placeholder="搜索任务..."
            onChange={e => handleSearch(e.target.value)}
            style={{ width: 200 }}
          />
          <Tooltip title="新建文件夹">
            <Button
              icon={<FolderAddOutlined />}
              onClick={() => handleCreate('folder', null)}
            />
          </Tooltip>
          <Tooltip title="新建任务">
            <Button
              icon={<FileAddOutlined />}
              onClick={() => handleCreate('task', null)}
            />
          </Tooltip>
          <Tooltip title="刷新">
            <Button
              icon={<ReloadOutlined />}
              onClick={loadTaskTree}
              loading={loading}
            />
          </Tooltip>
        </Space>
      </div>

      {/* 文件树 */}
      <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
        <DirectoryTree
          treeData={treeData}
          expandedKeys={expandedKeys}
          selectedKeys={selectedKeys}
          onExpand={setExpandedKeys}
          onSelect={handleSelect}
          onRightClick={({ node }) => setSelectedNode(node)}
          titleRender={renderTitle}
          showIcon
        />
      </div>

      {/* 创建任务/文件夹模态框 */}
      <Modal
        title={`新建${createType === 'folder' ? '文件夹' : '任务'}`}
        visible={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false)
          form.resetFields()
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateSubmit}
        >
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入名称' }]}
          >
            <Input placeholder={`输入${createType === 'folder' ? '文件夹' : '任务'}名称`} />
          </Form.Item>
          
          {createType === 'task' && (
            <>
              <Form.Item
                name="prompt"
                label="任务描述"
                rules={[{ required: true, message: '请输入任务描述' }]}
              >
                <TextArea
                  rows={4}
                  placeholder="描述任务的具体要求..."
                />
              </Form.Item>
              
              <Form.Item
                name="readme"
                label="详细文档 (README)"
              >
                <TextArea
                  rows={6}
                  placeholder="任务的详细说明、背景信息、注意事项等..."
                />
              </Form.Item>
            </>
          )}
          
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
    </div>
  )
}

export default TaskFileExplorer