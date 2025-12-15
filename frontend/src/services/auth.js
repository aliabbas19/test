import api from './api'
import { getDeviceFingerprint, setAuthToken } from '../utils/helpers'

export const login = async (username, password) => {
  const deviceFingerprint = getDeviceFingerprint()

  const response = await api.post('/api/auth/login', {
    username,
    password,
    device_fingerprint: deviceFingerprint,
  })

  const { access_token, refresh_token } = response.data

  // Store tokens
  localStorage.setItem('access_token', access_token)
  localStorage.setItem('refresh_token', refresh_token)

  // Store auth_token from response if available (primary method)
  if (response.data.auth_token) {
    setAuthToken(response.data.auth_token)
  } else {
    // Fallback: Store auth_token from cookie if available
    const authTokenCookie = document.cookie
      .split('; ')
      .find(row => row.startsWith('auth_token='))
    if (authTokenCookie) {
      const authToken = authTokenCookie.split('=')[1]
      setAuthToken(authToken)
    }
  }

  return response.data
}

export const autoLogin = async () => {
  const deviceFingerprint = getDeviceFingerprint()
  const authToken = localStorage.getItem('auth_token')

  if (!authToken) {
    throw new Error('No auth token found')
  }

  const response = await api.post('/api/auth/auto-login', {
    device_fingerprint: deviceFingerprint,
    auth_token: authToken,
  })

  const { access_token, refresh_token } = response.data

  // Store tokens
  localStorage.setItem('access_token', access_token)
  localStorage.setItem('refresh_token', refresh_token)

  return response.data
}

export const logout = async () => {
  await api.post('/api/auth/logout')
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('auth_token')
}

export const refreshToken = async () => {
  const refresh_token = localStorage.getItem('refresh_token')
  if (!refresh_token) throw new Error('No refresh token')

  const response = await api.post('/api/auth/refresh', {
    refresh_token,
  })

  const { access_token, refresh_token: new_refresh_token } = response.data
  localStorage.setItem('access_token', access_token)
  localStorage.setItem('refresh_token', new_refresh_token)

  return response.data
}

