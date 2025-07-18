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

// 统一 API V2 - 简化接口
export const unifiedApi = {
  // 快速创建并执行任务
  quickTask: (repoId, taskData) => 
    apiClient.post(`/v2/repos/${repoId}/quick-task`, taskData),
  
  // 获取仓库的所有分支（包含任务信息）
  listBranches: (repoId) => 
    apiClient.get(`/v2/repos/${repoId}/branches`),
  
  // 获取简化的仪表板数据
  getDashboard: () => 
    apiClient.get('/v2/dashboard'),
  
  // 获取迁移状态
  getMigrationStatus: () => 
    apiClient.get('/v2/migrate/status'),
  
  // 获取简化的设置
  getSimplifiedSettings: () => 
    apiClient.post('/v2/settings/simplify')
}

export const projectApi = {
  listProjects: (filter = 'all') => apiClient.get('/projects', { params: { filter } }),
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
  // 权限管理
  getProjectPermissions: (projectId) => apiClient.get(`/projects/${projectId}/permissions`),
  grantProjectPermission: (projectId, userId, role) => 
    apiClient.post(`/projects/${projectId}/permissions`, { user_id: userId, role }),
  revokeProjectPermission: (projectId, userId) => 
    apiClient.delete(`/projects/${projectId}/permissions`, { params: { user_id: userId } }),
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
  // Agent指标相关
  getAgentMetrics: () => apiClient.get('/metrics/agent'),
}

export const taskFileSystemApi = {
  // 任务文件系统API
  getTaskTree: (path = '/', maxDepth = -1) => 
    apiClient.get('/taskfs/tree', { params: { path, max_depth: maxDepth } }),
  listDirectory: (path = '/') => 
    apiClient.get('/taskfs/list', { params: { path } }),
  getTask: (path) => 
    apiClient.get('/taskfs/task', { params: { path } }),
  createTask: (data) => 
    apiClient.post('/taskfs/create', data),
  moveTask: (sourcePath, destParentPath, newName) => 
    apiClient.post('/taskfs/move', { source_path: sourcePath, dest_parent_path: destParentPath, new_name: newName }),
  deleteTask: (path, recursive = false) => 
    apiClient.delete('/taskfs/delete', { params: { path, recursive } }),
  executeTask: (path) => 
    apiClient.post('/taskfs/execute', { path }),
  searchTasks: (query, path = '/') => 
    apiClient.get('/taskfs/search', { params: { q: query, path } }),
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
  adminRegisterUser: (data) => apiClient.post('/auth/admin/users/register', data),
  updateUserClaudeToken: (userId, claudeToken) => 
    apiClient.put(`/auth/admin/users/${userId}/claude-token`, { claude_token: claudeToken }),
}

export const adminApi = {
  // 管理员API
  deleteUser: (userId) => apiClient.delete(`/admin/users/${userId}`),
  getAllTasks: () => apiClient.get('/admin/tasks'),
  getAllProjects: () => apiClient.get('/admin/projects'),
}

export const configApi = {
  // 配置管理
  getConfigs: (category) => apiClient.get('/configs', { params: { category } }),
  getConfig: (key) => apiClient.get(`/configs/${key}`),
  updateConfigs: (configs) => apiClient.put('/configs', { configs }),
  updateConfig: (key, value) => apiClient.put(`/configs/${key}`, { value }),
  deleteConfig: (key) => apiClient.delete(`/configs/${key}`),
  resetConfigs: () => apiClient.post('/configs/reset'),
  exportConfigs: () => apiClient.get('/configs/export'),
}

export const repositoryApi = {
  // 仓库管理
  listRepositories: () => apiClient.get('/repos'),
  createRepository: (data) => apiClient.post('/repos', data),
  getRepository: (repoId) => apiClient.get(`/repos/${repoId}`),
  updateRepository: (repoId, data) => apiClient.put(`/repos/${repoId}`, data),
  deleteRepository: (repoId) => apiClient.delete(`/repos/${repoId}`),
  
  // GitHub 集成
  importRepository: (data) => apiClient.post('/repos/import', data),
  syncRepository: (repoId) => apiClient.post(`/repos/${repoId}/sync`),
  
  // 分支管理
  createBranch: (repoId, data) => apiClient.post(`/repos/${repoId}/branches`, data),
  listBranches: (repoId) => apiClient.get(`/repos/${repoId}/branches`),
  executeBranch: (branchId) => apiClient.post(`/branches/${branchId}/execute`),
  
  // 议题管理
  createIssue: (repoId, data) => apiClient.post(`/repos/${repoId}/issues`, data),
  listIssues: (repoId) => apiClient.get(`/repos/${repoId}/issues`),
  updateIssue: (issueId, data) => apiClient.put(`/issues/${issueId}`, data),
  
  // Git 操作
  commitChanges: (repoId, data) => apiClient.post(`/repos/${repoId}/commit`, data),
  pushToRemote: (repoId) => apiClient.post(`/repos/${repoId}/push`),
  pullFromRemote: (repoId) => apiClient.post(`/repos/${repoId}/pull`),
  createPullRequest: (branchId, data) => apiClient.post(`/branches/${branchId}/pr`, data),
}

export default apiClient