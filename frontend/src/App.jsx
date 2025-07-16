import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import MainLayout from './components/layout/MainLayout'
import Dashboard from './pages/Dashboard'
import ProjectPage from './pages/ProjectPage'
import TasksPage from './pages/TasksPage'
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
      <Router>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="project/:projectName" element={<ProjectPage />} />
            <Route path="tasks" element={<TasksPage />} />
          </Route>
        </Routes>
      </Router>
    </ConfigProvider>
  )
}

export default App