import { createContext, useState, useEffect, useContext } from 'react'
import { login as loginApi, logout as logoutApi, autoLogin as autoLoginApi } from '../services/auth'
import { getAuthToken } from '../utils/helpers'
import api from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Try auto-login first if auth_token exists
    const authToken = getAuthToken()
    const accessToken = localStorage.getItem('access_token')
    
    if (authToken && !accessToken) {
      // Try auto-login
      autoLoginApi()
        .then(() => {
          fetchUser()
        })
        .catch(() => {
          // Auto-login failed
          setLoading(false)
        })
    } else if (accessToken) {
      // Fetch user info
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await api.get('/api/users/me')
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const data = await loginApi(username, password)
      await fetchUser()
      return data
    } catch (error) {
      throw error
    }
  }

  const logout = async () => {
    try {
      await logoutApi()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

