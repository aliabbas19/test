import axios from 'axios'

// In production, use empty string for relative URLs (same origin)
// In development, optionally set VITE_API_URL to backend URL
let API_URL = import.meta.env.PROD ? '' : (import.meta.env.VITE_API_URL ?? '')

// Runtime safety: If we are on the production domain (HTTPS), FORCE relative path
// This handles cases where build flags might be misconfigured or .env leaked
if (typeof window !== 'undefined' && window.location.hostname.includes('basamaljanaby.com')) {
  API_URL = ''
}

const api = axios.create({
  baseURL: API_URL,
  // Don't set Content-Type here - let Axios set it automatically
  // For JSON requests, it will use application/json
  // For FormData requests, it will use multipart/form-data
  withCredentials: true,
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(
            `${API_URL}/api/auth/refresh`,
            { refresh_token: refreshToken },
            { withCredentials: true }
          )

          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError)
        localStorage.clear() // Ruthless clearing
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // If 401 and it wasn't a refresh attempt (or we already retried), force logout
    if (error.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export default api

