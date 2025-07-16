import React, { useState } from 'react';
import { Card, List, Button, Tag, Modal, Form, Input, Select, message } from 'antd';
import { PlayCircleOutlined, EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;

const defaultTemplates = [
  {
    id: 'fix-bugs',
    name: '修复Bug',
    category: 'debug',
    prompt: '请帮我查找并修复代码中的bug。运行测试并确保所有测试通过。',
    tags: ['bug修复', '测试']
  },
  {
    id: 'add-feature',
    name: '添加新功能',
    category: 'feature',
    prompt: '请帮我实现以下功能：[功能描述]。确保代码符合项目规范。',
    tags: ['功能开发']
  },
  {
    id: 'refactor',
    name: '代码重构',
    category: 'refactor',
    prompt: '请重构这段代码，提高可读性和性能。保持原有功能不变。',
    tags: ['重构', '优化']
  },
  {
    id: 'write-tests',
    name: '编写测试',
    category: 'test',
    prompt: '请为这个模块编写单元测试，确保测试覆盖率达到80%以上。',
    tags: ['测试', '质量保证']
  },
  {
    id: 'create-component',
    name: '创建React组件',
    category: 'frontend',
    prompt: '创建一个React组件，名称为[组件名]，功能是[功能描述]。使用TypeScript和Ant Design。',
    tags: ['React', '组件']
  },
  {
    id: 'api-endpoint',
    name: '创建API端点',
    category: 'backend',
    prompt: '创建一个REST API端点：[HTTP方法] [路径]，功能是[功能描述]。包含输入验证和错误处理。',
    tags: ['API', '后端']
  },
  {
    id: 'optimize-performance',
    name: '性能优化',
    category: 'performance',
    prompt: '分析并优化代码性能。找出性能瓶颈并提供优化方案。',
    tags: ['性能', '优化']
  },
  {
    id: 'security-audit',
    name: '安全审计',
    category: 'security',
    prompt: '对代码进行安全审计，查找潜在的安全漏洞并修复。',
    tags: ['安全', '审计']
  }
];

const categoryColors = {
  debug: 'red',
  feature: 'blue',
  refactor: 'orange',
  test: 'green',
  frontend: 'purple',
  backend: 'cyan',
  performance: 'gold',
  security: 'magenta'
};

const TaskTemplates = ({ onUseTemplate }) => {
  const [templates, setTemplates] = useState(() => {
    const saved = localStorage.getItem('taskTemplates');
    return saved ? JSON.parse(saved) : defaultTemplates;
  });
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [form] = Form.useForm();

  const saveTemplates = (newTemplates) => {
    setTemplates(newTemplates);
    localStorage.setItem('taskTemplates', JSON.stringify(newTemplates));
  };

  const handleCreateOrUpdate = (values) => {
    if (editingTemplate) {
      // 更新模板
      const updated = templates.map(t => 
        t.id === editingTemplate.id ? { ...t, ...values } : t
      );
      saveTemplates(updated);
      message.success('模板更新成功');
    } else {
      // 创建新模板
      const newTemplate = {
        id: `custom-${Date.now()}`,
        ...values,
        tags: values.tags.split(',').map(t => t.trim()).filter(Boolean)
      };
      saveTemplates([...templates, newTemplate]);
      message.success('模板创建成功');
    }
    setModalVisible(false);
    form.resetFields();
    setEditingTemplate(null);
  };

  const handleEdit = (template) => {
    setEditingTemplate(template);
    form.setFieldsValue({
      ...template,
      tags: template.tags.join(', ')
    });
    setModalVisible(true);
  };

  const handleDelete = (templateId) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个模板吗？',
      onOk: () => {
        const filtered = templates.filter(t => t.id !== templateId);
        saveTemplates(filtered);
        message.success('模板已删除');
      }
    });
  };

  const handleUseTemplate = (template) => {
    if (onUseTemplate) {
      onUseTemplate(template.prompt);
      message.success('模板已应用');
    }
  };

  return (
    <>
      <Card 
        title="任务模板" 
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingTemplate(null);
              form.resetFields();
              setModalVisible(true);
            }}
          >
            新建模板
          </Button>
        }
      >
        <List
          dataSource={templates}
          renderItem={(template) => (
            <List.Item
              actions={[
                <Button
                  type="text"
                  icon={<PlayCircleOutlined />}
                  onClick={() => handleUseTemplate(template)}
                >
                  使用
                </Button>,
                <Button
                  type="text"
                  icon={<EditOutlined />}
                  onClick={() => handleEdit(template)}
                >
                  编辑
                </Button>,
                template.id.startsWith('custom-') && (
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleDelete(template.id)}
                  >
                    删除
                  </Button>
                )
              ].filter(Boolean)}
            >
              <List.Item.Meta
                title={
                  <span>
                    {template.name}{' '}
                    <Tag color={categoryColors[template.category]}>
                      {template.category}
                    </Tag>
                  </span>
                }
                description={
                  <>
                    <div>{template.prompt}</div>
                    <div style={{ marginTop: 8 }}>
                      {template.tags.map(tag => (
                        <Tag key={tag} style={{ marginTop: 4 }}>{tag}</Tag>
                      ))}
                    </div>
                  </>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      <Modal
        title={editingTemplate ? '编辑模板' : '创建新模板'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingTemplate(null);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateOrUpdate}
        >
          <Form.Item
            name="name"
            label="模板名称"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="例如：修复TypeScript类型错误" />
          </Form.Item>

          <Form.Item
            name="category"
            label="类别"
            rules={[{ required: true, message: '请选择类别' }]}
          >
            <Select placeholder="选择类别">
              {Object.keys(categoryColors).map(category => (
                <Option key={category} value={category}>
                  {category}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="prompt"
            label="提示语模板"
            rules={[{ required: true, message: '请输入提示语模板' }]}
            help="使用 [占位符] 来标记需要替换的部分"
          >
            <TextArea 
              rows={4} 
              placeholder="例如：请帮我创建一个 [组件类型] 组件，名称为 [组件名称]"
            />
          </Form.Item>

          <Form.Item
            name="tags"
            label="标签"
            help="多个标签用逗号分隔"
          >
            <Input placeholder="例如：React, 组件开发, TypeScript" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              {editingTemplate ? '更新模板' : '创建模板'}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default TaskTemplates;