import React, { useState } from 'react';
import { Upload, Button, message } from 'antd';
import { InboxOutlined, UploadOutlined } from '@ant-design/icons';
import { uploadFile } from '../services/api';

const { Dragger } = Upload;

const FileUpload = ({ projectName, onUploadSuccess, mode = 'button' }) => {
  const [uploading, setUploading] = useState(false);

  const customRequest = async ({ file, onProgress, onSuccess, onError }) => {
    setUploading(true);
    
    try {
      // 创建 FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project_name', projectName);
      
      // 调用上传 API
      const response = await uploadFile(formData, {
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress({ percent });
        }
      });
      
      message.success(`${file.name} 上传成功`);
      onSuccess(response.data);
      
      // 回调父组件
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
    } catch (error) {
      message.error(`${file.name} 上传失败: ${error.response?.data?.error || error.message}`);
      onError(error);
    } finally {
      setUploading(false);
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: true,
    customRequest,
    showUploadList: {
      showDownloadIcon: false,
      showRemoveIcon: true,
    },
    beforeUpload: (file) => {
      // 文件大小限制 (16MB)
      const isLt16M = file.size / 1024 / 1024 < 16;
      if (!isLt16M) {
        message.error('文件大小不能超过 16MB!');
        return false;
      }
      return true;
    }
  };

  if (mode === 'dragger') {
    return (
      <Dragger {...uploadProps} disabled={uploading}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p className="ant-upload-hint">
          支持单个或批量上传，文件大小限制为 16MB
        </p>
      </Dragger>
    );
  }

  return (
    <Upload {...uploadProps}>
      <Button icon={<UploadOutlined />} loading={uploading}>
        上传文件
      </Button>
    </Upload>
  );
};

export default FileUpload;