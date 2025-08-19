import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/auth/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data: { email: string; username: string; password: string; password_confirm: string }) =>
    api.post('/auth/register/', data),
  
  verify: (email: string, code: string) =>
    api.post('/auth/verify/', { email, verification_code: code }),
  
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login/', data),
  
  logout: () => api.post('/auth/logout/'),
  
  refreshToken: () => api.post('/auth/refresh/'),
}

export const profileAPI = {
  getProfile: () => api.get('/profiles/me/'),
  
  updateProfile: (data: any) => api.patch('/profiles/me/', data),
  
  createProfile: (data: any) => api.post('/profiles/', data),
  
  uploadPortfolio: (formData: FormData) =>
    api.post('/profiles/portfolio/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  browseProfiles: (params: any) => api.get('/profiles/browse/', { params }),
  
  getProfileStats: () => api.get('/profiles/me/stats/'),
}

export const subscriptionAPI = {
  getPlans: () => api.get('/subscriptions/plans/'),
  
  getSubscription: () => api.get('/subscriptions/me/'),
  
  createSubscription: (data: any) => api.post('/subscriptions/create/', data),
  
  cancelSubscription: () => api.post('/subscriptions/cancel/'),
  
  purchaseAIPortfolio: (data: any) => api.post('/subscriptions/purchase-ai-portfolio/', data),
  
  getUsage: () => api.get('/subscriptions/usage/'),
}

export const chatAPI = {
  getChats: () => api.get('/chat/'),
  
  getMessages: (chatId: string) => api.get(`/chat/${chatId}/messages/`),
  
  sendMessage: (chatId: string, data: any) => api.post(`/chat/${chatId}/messages/`, data),
  
  createChat: (data: any) => api.post('/chat/', data),
  
  translateMessage: (messageId: string, targetLanguage: string) =>
    api.post(`/chat/messages/${messageId}/translate/`, { target_language: targetLanguage }),
}

export const collaborationAPI = {
  getInvites: () => api.get('/collaborations/invites/'),
  
  sendInvite: (data: any) => api.post('/collaborations/invites/', data),
  
  respondToInvite: (inviteId: string, response: 'accept' | 'decline') =>
    api.post(`/collaborations/invites/${inviteId}/respond/`, { response }),
  
  getCollaborations: () => api.get('/collaborations/'),
  
  getSuggestions: () => api.get('/collaborations/suggestions/'),
}

export const aiAPI = {
  generateContent: (data: any) => api.post('/ai/generate/', data),
  
  validateContent: (data: any) => api.post('/ai/validate/', data),
  
  getCollaborationMatch: (profileId: string) =>
    api.get(`/ai/collaboration-match/${profileId}/`),
}

export default api
