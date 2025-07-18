import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true  // 启用 cookie 以支持会话
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 如果是401错误，跳转到登录页
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const projectApi = {
  listProjects: () => apiClient.get('/projects'),
  listAllProjects: () => apiClient.get('/admin/projects'),  // 管理员接口
  createProject: (name, initializeReadme = false) => 
    apiClient.post('/projects', { name, initialize_readme: initializeReadme }),
  getProjectDetails: (projectName) => apiClient.get(`/projects/${projectName}`),
  updateProject: (projectName, newPath) => apiClient.put(`/projects/${projectName}`, { new_path: newPath }),
  deleteProject: (projectName) => apiClient.delete(`/projects/${projectName}`),
  getFileContent: (filePath) => apiClient.get(`/files/${filePath}`),
  updateFileContent: (filePath, content) => apiClient.put(`/files/${filePath}`, { content }),
  deleteFile: (filePath) => apiClient.delete(`/files/${filePath}`),
  uploadFile: (formData) => apiClient.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

// Export individual functions for convenience
export const uploadFile = projectApi.uploadFile

export const taskApi = {
  executeTask: (prompt, projectPath) => 
    apiClient.post('/execute', { prompt, project_path: projectPath }),
  listTasks: () => apiClient.get('/tasks'),
  listAllTasks: () => apiClient.get('/admin/tasks'),  // 管理员接口
  getTask: (taskId) => apiClient.get(`/tasks/${taskId}`),
  cancelTask: (taskId) => apiClient.post(`/tasks/${taskId}/cancel`),
  // 任务链相关
  createTaskChain: (data) => apiClient.post('/task-chains', data),
  getTaskChildren: (taskId) => apiClient.get(`/tasks/${taskId}/children`),
  addChildTask: (taskId, prompt) => apiClient.post(`/tasks/${taskId}/add-child`, { prompt }),
  // 本地执行相关
  launchLocalExecution: (taskId) => apiClient.post(`/tasks/${taskId}/launch-local`),
  executeLocal: (prompt, projectPath) => 
    apiClient.post('/execute-local', { prompt, project_path: projectPath }),
}

export const authApi = {
  // 认证相关
  login: (data) => apiClient.post('/auth/login', data),
  register: (data) => apiClient.post('/auth/register', data),
  logout: () => apiClient.post('/auth/logout'),
  getCurrentUser: () => apiClient.get('/auth/me'),
  getConfig: () => apiClient.get('/auth/config'),
  
  // 管理员接口
  getAdminConfig: () => apiClient.get('/auth/admin/config'),
  updateAdminConfig: (data) => apiClient.put('/auth/admin/config', data),
  listUsers: () => apiClient.get('/auth/admin/users'),
  makeUserAdmin: (userId) => apiClient.post(`/auth/admin/users/${userId}/make-admin`),
}

export default apiClient