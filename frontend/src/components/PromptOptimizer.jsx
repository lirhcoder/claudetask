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
    '不要等待',
    '立即处理',
    '无需确认',
    '自动完成',
  ];

  // 常见的交互场景和解决方案
  const interactionScenarios = [
    {
      scenario: '文件覆盖确认',
      problem: '当文件已存在时，Claude 会询问是否覆盖',
      solution: '在提示中明确说明"如果文件已存在，直接覆盖，不要询问"',
      keywords: ['覆盖', '替换', '文件存在', '写入文件', '创建文件', '保存']
    },
    {
      scenario: '删除确认',
      problem: '删除文件或目录时需要确认',
      solution: '添加"确认删除，不需要再次询问"',
      keywords: ['删除', '移除', 'delete', 'remove', '清理']
    },
    {
      scenario: '创建目录',
      problem: '创建嵌套目录时可能需要确认',
      solution: '使用"递归创建所需的所有目录，包括父目录"',
      keywords: ['创建目录', '创建文件夹', 'mkdir', '目录结构']
    },
    {
      scenario: '选择选项',
      problem: '当有多个选项时，Claude 会让用户选择',
      solution: '明确指定"使用最合适的选项"或"选择第一个可用的选项"',
      keywords: ['选择', '选项', '多个', '哪个', '哪种']
    },
    {
      scenario: '继续执行',
      problem: 'Claude 可能会询问是否继续',
      solution: '添加"遇到任何问题请继续执行，不要停止"',
      keywords: ['继续', '执行', '运行', '处理', '操作']
    },
    {
      scenario: '错误处理',
      problem: '遇到错误时可能询问如何处理',
      solution: '明确说明"遇到错误时记录错误并继续，不要中断"',
      keywords: ['错误', '失败', '异常', 'error', '问题']
    },
    {
      scenario: 'Git操作',
      problem: 'Git操作可能需要确认',
      solution: '添加"Git操作不需要确认，直接执行commit和push"',
      keywords: ['git', '提交', 'commit', 'push', '版本控制']
    },
    {
      scenario: '安装依赖',
      problem: '安装包时可能需要确认',
      solution: '使用"自动安装所有依赖，使用默认配置"',
      keywords: ['安装', 'install', 'npm', 'pip', '依赖', 'package']
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
      optimized = `${originalPrompt}

【非交互模式指令】
1. 不要询问任何确认，直接执行所有操作
2. 文件操作：如果文件已存在，直接覆盖；如果目录不存在，递归创建
3. 选择处理：遇到多个选项时，选择最合适或第一个可用的选项
4. 错误处理：遇到非致命错误时，记录错误并继续执行，不要中断
5. 默认行为：所有操作使用默认配置，不要等待用户输入
6. 持续执行：完成一个任务后，自动继续下一个任务，直到全部完成`;
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
          description="Claude Code 在 Web 环境下运行时无法响应确认提示或选择选项。由于 Claude CLI 不支持 --yes 等命令行参数，必须在提示语中明确指定所有非交互行为，才能避免执行失败。"
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