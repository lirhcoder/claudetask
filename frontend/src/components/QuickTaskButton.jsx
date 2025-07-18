import React, { useState } from 'react';
import { Button, Modal, Form, Input, Select, message, Space } from 'antd';
import { PlusOutlined, ThunderboltOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TextArea } = Input;
const { Option } = Select;

const QuickTaskButton = ({ repositoryId, onTaskCreated }) => {
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `/api/v2/repos/${repositoryId}/quick-task`,
        {
          title: values.title,
          description: values.description,
          prompt: values.prompt || values.title,
          executor_type: values.executor_type || 'claude',
          auto_commit: values.auto_commit !== false,
          auto_pr: values.auto_pr === true,
          files: values.files ? values.files.split(',').map(f => f.trim()) : []
        }
      );

      if (response.data.success) {
        message.success('任务创建并执行成功！');
        setVisible(false);
        form.resetFields();
        if (onTaskCreated) {
          onTaskCreated(response.data);
        }
      }
    } catch (error) {
      message.error(error.response?.data?.error || '任务执行失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        type="primary"
        icon={<ThunderboltOutlined />}
        onClick={() => setVisible(true)}
        size="large"
      >
        快速任务
      </Button>

      <Modal
        title="创建并执行任务"
        visible={visible}
        onCancel={() => setVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            executor_type: 'claude',
            auto_commit: true,
            auto_pr: false
          }}
        >
          <Form.Item
            name="title"
            label="任务标题"
            rules={[{ required: true, message: '请输入任务标题' }]}
          >
            <Input placeholder="例如：修复登录页面的样式问题" />
          </Form.Item>

          <Form.Item
            name="prompt"
            label="执行提示词"
            tooltip="留空则使用标题作为提示词"
          >
            <TextArea
              rows={3}
              placeholder="详细描述需要执行的操作..."
            />
          </Form.Item>

          <Form.Item
            name="description"
            label="任务描述"
          >
            <TextArea
              rows={2}
              placeholder="可选的详细描述..."
            />
          </Form.Item>

          <Form.Item
            name="files"
            label="相关文件"
            tooltip="逗号分隔的文件路径"
          >
            <Input placeholder="例如：src/login.js, src/styles/login.css" />
          </Form.Item>

          <Space size="large" style={{ width: '100%' }}>
            <Form.Item
              name="executor_type"
              label="执行器"
              style={{ marginBottom: 0 }}
            >
              <Select style={{ width: 120 }}>
                <Option value="claude">Claude</Option>
                <Option value="local">本地</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="auto_commit"
              label="自动提交"
              valuePropName="checked"
              style={{ marginBottom: 0 }}
            >
              <Select style={{ width: 100 }}>
                <Option value={true}>是</Option>
                <Option value={false}>否</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="auto_pr"
              label="自动创建PR"
              valuePropName="checked"
              style={{ marginBottom: 0 }}
            >
              <Select style={{ width: 100 }}>
                <Option value={true}>是</Option>
                <Option value={false}>否</Option>
              </Select>
            </Form.Item>
          </Space>

          <Form.Item style={{ marginTop: 24, marginBottom: 0 }}>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                创建并执行
              </Button>
              <Button onClick={() => setVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default QuickTaskButton;