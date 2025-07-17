import React, { useState } from 'react';
import { Modal, Button, Alert, Space, Tag, Tooltip } from 'antd';
import { BulbOutlined, QuestionCircleOutlined } from '@ant-design/icons';

const PromptOptimizer = ({ visible, onClose, onOptimize, originalPrompt }) => {
  const [optimizedPrompt, setOptimizedPrompt] = useState('');

  // 非交互模式的关键词
  const nonInteractiveKeywords = [
    '不要询问确认',
    '自动执行所有操作',
    '不需要用户输入',
    '静默模式',
    '非交互式',
    '自动选择默认值',
    '跳过所有提示',
    '直接执行',
  ];

  // 常见的交互场景和解决方案
  const interactionScenarios = [
    {
      scenario: '文件覆盖确认',
      problem: '当文件已存在时，Claude 会询问是否覆盖',
      solution: '在提示中明确说明"如果文件已存在，直接覆盖"',
      keywords: ['覆盖', '替换', '不询问']
    },
    {
      scenario: '删除确认',
      problem: '删除文件或目录时需要确认',
      solution: '添加"确认删除，不需要再次询问"',
      keywords: ['确认删除', '直接删除']
    },
    {
      scenario: '创建目录',
      problem: '创建嵌套目录时可能需要确认',
      solution: '使用"递归创建所需的所有目录"',
      keywords: ['递归创建', '自动创建父目录']
    },
    {
      scenario: '选择选项',
      problem: '当有多个选项时，Claude 会让用户选择',
      solution: '明确指定选择哪个选项，如"使用第一个选项"或"选择默认值"',
      keywords: ['默认选项', '第一个', '自动选择']
    }
  ];

  const optimizePrompt = () => {
    let optimized = originalPrompt;
    
    // 检查是否已包含非交互关键词
    const hasNonInteractiveKeyword = nonInteractiveKeywords.some(keyword => 
      originalPrompt.includes(keyword)
    );

    if (!hasNonInteractiveKeyword) {
      // 添加通用的非交互指令
      optimized = `${originalPrompt}\n\n注意：请在非交互模式下执行，不要询问任何确认，自动处理所有操作。如果遇到选择，使用默认值或最合理的选项。`;
    }

    // 检测可能的交互场景
    const detectedScenarios = interactionScenarios.filter(scenario => {
      const promptLower = originalPrompt.toLowerCase();
      return scenario.keywords.some(keyword => promptLower.includes(keyword.toLowerCase()));
    });

    if (detectedScenarios.length > 0) {
      optimized += '\n\n具体要求：';
      detectedScenarios.forEach(scenario => {
        optimized += `\n- ${scenario.solution}`;
      });
    }

    setOptimizedPrompt(optimized);
  };

  React.useEffect(() => {
    if (visible && originalPrompt) {
      optimizePrompt();
    }
  }, [visible, originalPrompt]);

  return (
    <Modal
      title={
        <Space>
          <BulbOutlined />
          提示语优化建议
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={700}
      footer={[
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button
          key="apply"
          type="primary"
          onClick={() => {
            onOptimize(optimizedPrompt);
            onClose();
          }}
        >
          应用优化
        </Button>
      ]}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Alert
          message="为什么需要优化提示语？"
          description="Claude Code 在 Web 环境下以非交互模式运行，无法响应确认提示或选择选项。优化提示语可以避免因交互需求导致的执行失败。"
          type="info"
          showIcon
        />

        <div>
          <h4>原始提示语：</h4>
          <div style={{ 
            padding: '12px', 
            background: '#f5f5f5', 
            borderRadius: '4px',
            marginBottom: '16px'
          }}>
            {originalPrompt}
          </div>
        </div>

        <div>
          <h4>优化后的提示语：</h4>
          <div style={{ 
            padding: '12px', 
            background: '#e6f7ff', 
            borderRadius: '4px',
            border: '1px solid #91d5ff'
          }}>
            <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{optimizedPrompt}</pre>
          </div>
        </div>

        <div>
          <h4>优化建议：</h4>
          <Space direction="vertical" style={{ width: '100%' }}>
            {nonInteractiveKeywords.slice(0, 4).map((keyword, index) => (
              <Tag key={index} color="blue">
                {keyword}
              </Tag>
            ))}
            <Tooltip title="在提示语中包含这些关键词可以避免交互问题">
              <QuestionCircleOutlined style={{ color: '#1890ff' }} />
            </Tooltip>
          </Space>
        </div>

        <Alert
          message="最佳实践"
          description={
            <ul style={{ marginBottom: 0 }}>
              <li>明确指定所有操作的行为（如文件存在时的处理方式）</li>
              <li>避免让 Claude 做选择，直接告诉它应该怎么做</li>
              <li>使用"自动"、"直接"、"不询问"等明确的指令</li>
              <li>对于可能的冲突情况，预先说明处理方式</li>
            </ul>
          }
          type="success"
          showIcon
        />
      </Space>
    </Modal>
  );
};

export default PromptOptimizer;