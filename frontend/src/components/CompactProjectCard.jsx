import React from 'react';
import { Card, Button, Dropdown, Space, Tooltip, Typography } from 'antd';
import { 
  FolderOpenOutlined, 
  MoreOutlined, 
  DeleteOutlined, 
  UploadOutlined,
  EditOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Text } = Typography;

const CompactProjectCard = ({ project, onDelete, onUpload, onEdit }) => {
  const navigate = useNavigate();

  const handleOpenProject = () => {
    navigate(`/project/${project.name}`);
  };

  const menuItems = [
    {
      key: 'upload',
      icon: <UploadOutlined />,
      label: '上传文件',
      onClick: () => onUpload && onUpload(project)
    },
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: '编辑路径',
      onClick: () => onEdit && onEdit(project)
    },
    {
      type: 'divider'
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: '删除项目',
      danger: true,
      onClick: () => onDelete && onDelete(project.name)
    }
  ];

  // 格式化路径，只显示最后两级
  const formatPath = (path) => {
    if (!path) return '';
    const parts = path.split(/[/\\]/);
    if (parts.length <= 2) return path;
    return '.../' + parts.slice(-2).join('/');
  };

  // 格式化时间为相对时间
  const formatRelativeTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return '刚刚';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} 分钟前`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} 小时前`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} 天前`;
    
    return date.toLocaleDateString('zh-CN');
  };

  return (
    <Card
      size="small"
      hoverable
      className="project-card"
      bodyStyle={{ padding: '12px' }}
      onClick={handleOpenProject}
      extra={
        <Dropdown
          menu={{ items: menuItems }}
          trigger={['click']}
          placement="bottomRight"
          onClick={(e) => e.stopPropagation()}
        >
          <Button
            type="text"
            size="small"
            icon={<MoreOutlined />}
            onClick={(e) => e.stopPropagation()}
          />
        </Dropdown>
      }
    >
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <FolderOpenOutlined style={{ fontSize: 16, color: '#1890ff' }} />
          <Text strong style={{ fontSize: 14, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {project.name}
          </Text>
        </div>
        
        <Tooltip title={project.absolute_path || project.path}>
          <Text type="secondary" style={{ fontSize: 12, display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {formatPath(project.absolute_path || project.path)}
          </Text>
        </Tooltip>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 4 }}>
          <CalendarOutlined style={{ fontSize: 12, color: '#8c8c8c' }} />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {formatRelativeTime(project.modified_at || project.created_at)}
          </Text>
        </div>
      </Space>
    </Card>
  );
};

export default CompactProjectCard;