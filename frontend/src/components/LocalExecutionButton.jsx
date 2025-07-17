import React, { useState } from 'react';
import { Button, Tooltip, Modal, Space, Alert, message } from 'antd';
import { DesktopOutlined, WindowsOutlined, AppleOutlined, CodeOutlined } from '@ant-design/icons';
import { taskApi } from '../services/api';

const LocalExecutionButton = ({ taskId, prompt, projectPath, size = 'small' }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [launching, setLaunching] = useState(false);

  const handleLaunchLocal = async () => {
    setLaunching(true);
    try {
      if (taskId) {
        // 启动已存在的任务
        await taskApi.launchLocalExecution(taskId);
      } else {
        // 创建新任务并启动
        await taskApi.executeLocal(prompt, projectPath);
      }
      
      message.success('已在本地终端启动任务');
      setModalVisible(false);
    } catch (error) {
      console.error('启动本地执行失败:', error);
      message.error(error.response?.data?.error || '启动失败');
    } finally {
      setLaunching(false);
    }
  };

  const detectOS = () => {
    const platform = navigator.platform.toLowerCase();
    if (platform.includes('win')) return 'windows';
    if (platform.includes('mac')) return 'macos';
    return 'linux';
  };

  const getOSIcon = () => {
    const os = detectOS();
    switch (os) {
      case 'windows':
        return <WindowsOutlined />;
      case 'macos':
        return <AppleOutlined />;
      default:
        return <CodeOutlined />;
    }
  };

  const getOSName = () => {
    const os = detectOS();
    switch (os) {
      case 'windows':
        return 'Windows Terminal / CMD';
      case 'macos':
        return 'Terminal.app';
      default:
        return 'Linux Terminal';
    }
  };

  const showConfirmModal = () => {
    setModalVisible(true);
  };

  return (
    <>
      <Tooltip title="在本地终端执行（支持交互）">
        <Button
          size={size}
          icon={<DesktopOutlined />}
          onClick={showConfirmModal}
          disabled={!prompt && !taskId}
        >
          本地执行
        </Button>
      </Tooltip>

      <Modal
        title={
          <Space>
            <DesktopOutlined />
            在本地终端执行任务
          </Space>
        }
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setModalVisible(false)}>
            取消
          </Button>,
          <Button
            key="launch"
            type="primary"
            icon={<DesktopOutlined />}
            onClick={handleLaunchLocal}
            loading={launching}
          >
            启动终端
          </Button>
        ]}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Alert
            message="本地终端执行模式"
            description="任务将在本地终端中执行，支持与 Claude 的完整交互。适合需要用户输入或确认的复杂任务。"
            type="info"
            showIcon
          />

          <div>
            <h4>即将启动：</h4>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <strong>终端类型：</strong> {getOSIcon()} {getOSName()}
              </div>
              <div>
                <strong>项目路径：</strong> {projectPath}
              </div>
              <div>
                <strong>任务提示：</strong>
                <div style={{ 
                  marginTop: 8,
                  padding: 12, 
                  background: '#f5f5f5', 
                  borderRadius: 4,
                  maxHeight: 120,
                  overflow: 'auto'
                }}>
                  {prompt || '使用已保存的任务提示'}
                </div>
              </div>
            </Space>
          </div>

          <Alert
            message="注意事项"
            description={
              <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                <li>终端窗口会自动打开</li>
                <li>您可以在终端中与 Claude 交互</li>
                <li>任务完成后按任意键关闭终端</li>
                <li>执行结果不会实时同步到 Web 界面</li>
              </ul>
            }
            type="warning"
          />
        </Space>
      </Modal>
    </>
  );
};

export default LocalExecutionButton;