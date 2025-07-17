import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
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
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const projectApi = {
  listProjects: () => apiClient.get('/projects'),
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

export default apiClient