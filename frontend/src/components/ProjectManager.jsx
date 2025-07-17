import React, { useState } from 'react';
import { Card, Button, Space, Modal, Form, Input, Switch, message, Popconfirm } from 'antd';
import { FolderAddOutlined, DeleteOutlined, EditOutlined, FolderOpenOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import FileUpload from './FileUpload';

const ProjectManager = ({ project, onProjectUpdate, onProjectDelete }) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const navigate = useNavigate();

  const handleOpenProject = () => {
    navigate(`/project/${project.name}`);
  };

  const handleDeleteProject = () => {
    if (onProjectDelete) {
      onProjectDelete(project.name);
    }
  };

  const handleUploadSuccess = () => {
    setUploadModalVisible(false);
    message.success('文件上传成功');
    if (onProjectUpdate) {
      onProjectUpdate();
    }
  };

  return (
    <>
      <Card
        hoverable
        size="small"
        actions={[
          <Button
            type="text"
            size="small"
            icon={<FolderOpenOutlined />}
            onClick={handleOpenProject}
            title="打开项目"
          />,
          <Button
            type="text"
            size="small"
            icon={<FolderAddOutlined />}
            onClick={() => setUploadModalVisible(true)}
            title="上传文件"
          />,
          <Popconfirm
            title="确定要删除这个项目吗？"
            description="此操作不可撤销"
            onConfirm={handleDeleteProject}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              size="small"
              danger
              icon={<DeleteOutlined />}
              title="删除项目"
            />
          </Popconfirm>
        ]}
      >
        <Card.Meta
          title={
            <div style={{ fontSize: '14px', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {project.name}
            </div>
          }
          description={
            <div style={{ fontSize: '12px', color: '#666' }}>
              <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {project.absolute_path || project.path}
              </div>
              <div style={{ marginTop: 4 }}>
                {new Date(project.created_at).toLocaleDateString()}
              </div>
            </div>
          }
        />
      </Card>

      <Modal
        title={`上传文件到 ${project.name}`}
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        footer={null}
        width={600}
      >
        <FileUpload
          projectName={project.name}
          onUploadSuccess={handleUploadSuccess}
          mode="dragger"
        />
      </Modal>
    </>
  );
};

export default ProjectManager;