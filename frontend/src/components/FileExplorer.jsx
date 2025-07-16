import React from 'react'
import { Tree } from 'antd'
import { FileOutlined, FolderOutlined } from '@ant-design/icons'

const FileExplorer = ({ files, onFileSelect }) => {
  const convertToTreeData = (files) => {
    return files.map(file => ({
      title: file.name,
      key: file.path,
      icon: file.type === 'directory' ? <FolderOutlined /> : <FileOutlined />,
      children: file.children ? convertToTreeData(file.children) : undefined,
      isLeaf: file.type !== 'directory',
      data: file
    }))
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