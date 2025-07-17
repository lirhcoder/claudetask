import React from 'react'
import { Tree, Dropdown, Modal, message } from 'antd'
import { FileOutlined, FolderOutlined, DeleteOutlined } from '@ant-design/icons'
import { projectApi } from '../services/api'

const FileExplorer = ({ files, onFileSelect, onFileDeleted }) => {
  const handleDelete = (file) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文件 "${file.name}" 吗？此操作不可撤销。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await projectApi.deleteFile(file.path)
          message.success('文件删除成功')
          if (onFileDeleted) {
            onFileDeleted(file)
          }
        } catch (error) {
          message.error('删除文件失败: ' + (error.response?.data?.error || error.message))
        }
      }
    })
  }

  const convertToTreeData = (files) => {
    return files.map(file => {
      const isFile = file.type !== 'directory'
      
      const menuItems = isFile ? [
        {
          label: '删除',
          key: 'delete',
          icon: <DeleteOutlined />,
          danger: true,
          onClick: () => handleDelete(file)
        }
      ] : []
      
      return {
        title: (
          <Dropdown
            menu={{ items: menuItems }}
            trigger={['contextMenu']}
            disabled={!isFile}
          >
            <span style={{ userSelect: 'none' }}>{file.name}</span>
          </Dropdown>
        ),
        key: file.path,
        icon: file.type === 'directory' ? <FolderOutlined /> : <FileOutlined />,
        children: file.children ? convertToTreeData(file.children) : undefined,
        isLeaf: isFile,
        data: file
      }
    })
  }

  const treeData = convertToTreeData(files)

  const handleSelect = (selectedKeys, { node }) => {
    if (node.data && onFileSelect) {
      onFileSelect(node.data)
    }
  }

  return (
    <Tree
      showIcon
      defaultExpandAll
      treeData={treeData}
      onSelect={handleSelect}
    />
  )
}

export default FileExplorer