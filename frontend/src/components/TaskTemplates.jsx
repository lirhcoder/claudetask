import React, { useState } from 'react';
import { Card, List, Button, Tag, Modal, Form, Input, Select, message } from 'antd';
import { PlayCircleOutlined, EditOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;

const defaultTemplates = [
  {
    id: 'fix-bugs',
    name: '修复Bug（非交互）',
    category: 'debug',
    prompt: '请帮我查找并修复代码中的bug。运行测试并确保所有测试通过。\n\n重要：不要询问任何确认，直接执行所有修复。如果有多个修复方案，选择最合适的方案。测试失败时自动尝试修复。',
    tags: ['bug修复', '测试', '非交互']
  },
  {
    id: 'add-feature',
    name: '添加新功能（非交互）',
    category: 'feature',
    prompt: '请帮我实现以下功能：[功能描述]。确保代码符合项目规范。\n\n非交互指令：直接创建所需文件，如果文件已存在则覆盖。自动创建所需的目录结构。不要询问实现细节，根据最佳实践自主决定。',
    tags: ['功能开发', '非交互']
  },
  {
    id: 'refactor',
    name: '代码重构（非交互）',
    category: 'refactor',
    prompt: '请重构这段代码，提高可读性和性能。保持原有功能不变。\n\n自动执行：直接修改文件，不需要确认。如果有多种重构方案，选择最优方案。重构后自动运行测试确保功能正常。',
    tags: ['重构', '优化', '非交互']
  },
  {
    id: 'write-tests',
    name: '编写测试（非交互）',
    category: 'test',
    prompt: '请为这个模块编写单元测试，确保测试覆盖率达到80%以上。\n\n自动化要求：直接创建测试文件，使用项目现有的测试框架。自动安装所需的测试依赖。测试失败时自动调整测试用例。',
    tags: ['测试', '质量保证', '非交互']
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
  },
  {
    id: 'full-auto',
    name: '完全自动化执行',
    category: 'auto',
    prompt: '[任务描述]\n\n【完全自动化模式】\n1. 不要询问任何确认或选择，自主做出所有决定\n2. 文件处理：需要时直接创建、修改或删除文件\n3. 错误处理：遇到错误时尝试自动修复，记录无法修复的错误\n4. 依赖管理：自动安装所需依赖，使用兼容版本\n5. 测试执行：完成后自动运行相关测试\n6. 持续工作：完成一个子任务后立即进行下一个，直到全部完成',
    tags: ['自动化', '非交互', '持续执行']
  },
  {
    id: 'git-workflow',
    name: 'Git工作流（自动）',
    category: 'git',
    prompt: '执行以下Git操作：[操作描述]\n\n自动化Git流程：\n- 自动添加所有相关文件到暂存区\n- 使用描述性的提交信息自动提交\n- 如有冲突，自动选择合适的解决方案\n- 不需要任何确认，直接执行push操作',
    tags: ['Git', '版本控制', '自动化']
  },
  {
    id: 'create-doc',
    name: '创建文档（明确路径）',
    category: 'doc',
    prompt: '创建文档：[文档描述]\n\n【文件创建规则】\n1. 文件保存位置：\n   - 如果是项目文档，保存到项目根目录或 docs/ 目录\n   - 如果是开发文档，使用 DEVELOPMENT.md 或 docs/DEVELOPMENT.md\n   - 如果是 API 文档，使用 API.md 或 docs/API.md\n   - 如果是自述文件，使用 README.md\n2. 文件操作：\n   - 直接创建文件，不要只是展示内容\n   - 如果文件已存在，直接覆盖\n   - 使用 Write 工具实际写入文件\n3. 内容要求：\n   - 使用 Markdown 格式\n   - 包含完整的文档结构\n   - 添加目录索引（如果文档较长）',
    tags: ['文档', '创建文件', '非交互']
  },
  {
    id: 'save-content',
    name: '保存内容到文件',
    category: 'file',
    prompt: '将以下内容保存到文件：[内容描述]\n\n【保存规则】\n1. 文件命名：\n   - 根据内容类型自动选择合适的文件名\n   - 使用适当的文件扩展名（.md, .txt, .json, .py 等）\n2. 保存位置：\n   - 明确指定路径：[指定路径，如 /path/to/file.ext]\n   - 如果未指定，根据内容类型选择：\n     * 配置文件 → 项目根目录\n     * 源代码 → src/ 或相应语言目录\n     * 文档 → docs/ 目录\n     * 测试 → tests/ 目录\n3. 执行要求：\n   - 使用 Write 工具直接创建文件\n   - 不要询问确认，直接保存\n   - 创建必要的目录结构',
    tags: ['文件操作', '保存', '非交互']
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
  security: 'magenta',
  auto: 'volcano',
  git: 'geekblue',
  doc: 'lime',
  file: 'orange'
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