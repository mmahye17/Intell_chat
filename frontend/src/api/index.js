import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 180000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => {
    const newToken = res.headers['x-new-access-token']
    if (newToken) localStorage.setItem('token', newToken)
    return res
  },
  err => {
    const msg = err.response?.data?.detail || err.response?.data?.message || '请求失败'
    ElMessage.error(msg)
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

// User
export const register = (username, password) =>
  api.post('/api/users/register', { username, password })
export const login = (username, password) =>
  api.post('/api/users/login', { username, password })
export const logout = () =>
  api.post('/api/users/logout', { username: '', password: '' })
export const getUserInfo = (userId) =>
  api.get(`/api/users/${userId}`)
export const updateUserInfo = (data) =>
  api.put('/api/users/user_info', data)

// Conversations
export const getConversationList = (mode = 'recent') =>
  api.get('/api/conversations/list', { params: { mode } })
export const getConversationDetail = (convId) =>
  api.get(`/api/conversations/${convId}`)
export const renameConversation = (convId, title) =>
  api.put(`/api/conversations/${convId}`, { title })
export const deleteConversation = (convId) =>
  api.delete(`/api/conversations/${convId}`)

// Chat
export const sendMessage = (query, convId = null, file = null, retrievalMode = 'vector') => {
  const form = new FormData()
  form.append('query', query)
  if (convId) form.append('conv_id', convId)
  if (file) form.append('file', file)
  form.append('retrieval_mode', retrievalMode)
  return api.post('/api/conversations/messages', form)
}

// Documents
export const getDocumentList = () => api.get('/api/documents/list')
export const deleteDocument = (docId) => api.delete(`/api/documents/${docId}`)

export default api
