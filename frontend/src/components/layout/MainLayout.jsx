import React, { useState, useEffect } from 'react'
import { Layout, Menu, Button, Space, Dropdown, Avatar, message } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  ProjectOutlined,
  DashboardOutlined,
  HistoryOutlined,
  MoonOutlined,
  SunOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  CrownOutlined,
  FolderOutlined,
  FolderOpenOutlined,
  FileTextOutlined,
  GithubOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import { useThemeStore } from '../../stores/themeStore'

const { Header, Sider, Content } = Layout

const MainLayout = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { isDarkMode, toggleTheme } = useThemeStore()
  const [collapsed, setCollapsed] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    // 获取当前用户信息
    loadCurrentUser()
  }, [])

  const loadCurrentUser = async () => {
    try {
      const { authApi } = await import('../../services/api')
      const data = await authApi.getCurrentUser()
      setCurrentUser(data.user)
    } catch (error) {
      // 未登录，跳转到登录页
      navigate('/login')
    }
  }

  const handleLogout = async () => {
    try {
      const { authApi } = await import('../../services/api')
      await authApi.logout()
      message.success('已退出登录')
      navigate('/login')
    } catch (error) {
      message.error('退出失败')
    }
  }

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '工作台',
    },
    {
      key: '/repositories',
      icon: <GithubOutlined />,
      label: '仓库',
    },
    {
      key: '/agent-index',
      icon: <ThunderboltOutlined />,
      label: '员工指数',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
    currentUser?.is_admin && {
      key: '/admin',
      icon: <CrownOutlined />,
      label: '管理员',
    },
  ].filter(Boolean)

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        width={200}
        collapsedWidth={80}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div
          style={{
            height: 32,
            margin: 16,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: collapsed ? 16 : 20,
            fontWeight: 'bold',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
          }}
        >
          {collapsed ? 'CC' : 'Claude Code'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout 
        style={{ 
          marginLeft: collapsed ? 80 : 200,
          transition: 'margin-left 0.2s',
          background: isDarkMode ? '#001529' : '#f0f2f5' 
        }}
      >
        <Header
          style={{
            padding: '0 16px',
            background: isDarkMode ? '#141414' : '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 1px 4px rgba(0,21,41,.08)',
            position: 'sticky',
            top: 0,
            zIndex: 1,
            width: '100%',
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{
              fontSize: '16px',
              width: 64,
              height: 64,
            }}
          />
          <Space>
            <Button
              type="text"
              icon={isDarkMode ? <SunOutlined /> : <MoonOutlined />}
              onClick={toggleTheme}
            />
            {currentUser && (
              <Dropdown
                menu={{
                  items: [
                    {
                      key: 'user',
                      label: (
                        <div>
                          <div>{currentUser.email}</div>
                          <div style={{ fontSize: 12, color: '#999' }}>
                            {currentUser.is_admin ? '管理员' : '普通用户'}
                          </div>
                        </div>
                      ),
                      disabled: true,
                    },
                    {
                      type: 'divider',
                    },
                    {
                      key: 'logout',
                      icon: <LogoutOutlined />,
                      label: '退出登录',
                      onClick: handleLogout,
                    },
                  ],
                }}
                placement="bottomRight"
              >
                <Avatar
                  style={{ cursor: 'pointer', backgroundColor: '#1890ff' }}
                  icon={<UserOutlined />}
                />
              </Dropdown>
            )}
          </Space>
        </Header>
        <Content
          style={{
            margin: '16px',
            minHeight: 'calc(100vh - 96px)',
            display: 'flex',
            justifyContent: 'center',
            overflow: 'auto',
          }}
        >
          <div
            style={{
              padding: 16,
              width: '100%',
              maxWidth: 1400,
              background: isDarkMode ? '#141414' : '#fff',
              borderRadius: 8,
            }}
          >
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout