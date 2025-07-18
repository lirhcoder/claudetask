import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ConfigProvider, theme, App as AntdApp } from 'antd'
import MainLayout from './components/layout/MainLayout'
import Dashboard from './pages/Dashboard'
import ProjectPage from './pages/ProjectPage'
import ProjectsPage from './pages/ProjectsPage'
import TasksPage from './pages/TasksPage'
import TaskWorkspace from './pages/TaskWorkspace'
import SettingsPage from './pages/SettingsPage'
import LoginPage from './pages/LoginPage'
import AdminPage from './pages/AdminPage'
import { useThemeStore } from './stores/themeStore'

function App() {
  const { isDarkMode } = useThemeStore()

  return (
    <ConfigProvider
      theme={{
        algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <AntdApp>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="projects" element={<ProjectsPage />} />
              <Route path="project/:projectName" element={<ProjectPage />} />
              <Route path="tasks" element={<TasksPage />} />
              <Route path="workspace/*" element={<TaskWorkspace />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="admin" element={<AdminPage />} />
            </Route>
          </Routes>
        </Router>
      </AntdApp>
    </ConfigProvider>
  )
}

export default App