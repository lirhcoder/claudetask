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
        actions={[
          <Button
            type="text"
            icon={<FolderOpenOutlined />}
            onClick={handleOpenProject}
          >
            打开
          </Button>,
          <Button
            type="text"
            icon={<FolderAddOutlined />}
            onClick={() => setUploadModalVisible(true)}
          >
            上传文件
          </Button>,
          <Popconfirm
            title="确定要删除这个项目吗？"
            description="此操作不可撤销"
            onConfirm={handleDeleteProject}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        ]}
      >
        <Card.Meta
          title={project.name}
          description={
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <div>路径: {project.path}</div>
              <div>创建时间: {new Date(project.created_at).toLocaleString()}</div>
              {project.last_modified && (
                <div>最后修改: {new Date(project.last_modified).toLocaleString()}</div>
              )}
            </Space>
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