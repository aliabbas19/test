export const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ar-EG', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

export const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleTimeString('ar-EG', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

export const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * Generate device fingerprint for device binding
 * Combines browser and device information
 */
export const generateDeviceFingerprint = () => {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  ctx.textBaseline = 'top'
  ctx.font = '14px Arial'
  ctx.fillText('Device fingerprint', 2, 2)
  
  const fingerprint = [
    navigator.userAgent,
    navigator.language,
    screen.width + 'x' + screen.height,
    new Date().getTimezoneOffset(),
    canvas.toDataURL(),
    navigator.hardwareConcurrency || '',
    navigator.deviceMemory || '',
    navigator.platform,
    window.location.href
  ].join('|')
  
  // Simple hash function
  let hash = 0
  for (let i = 0; i < fingerprint.length; i++) {
    const char = fingerprint.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  
  return Math.abs(hash).toString(36) + fingerprint.substring(0, 50)
}

/**
 * Get or generate device fingerprint and store in localStorage
 */
export const getDeviceFingerprint = () => {
  let fingerprint = localStorage.getItem('device_fingerprint')
  if (!fingerprint) {
    fingerprint = generateDeviceFingerprint()
    localStorage.setItem('device_fingerprint', fingerprint)
  }
  return fingerprint
}

/**
 * Get auth token from localStorage
 */
export const getAuthToken = () => {
  return localStorage.getItem('auth_token')
}

/**
 * Store auth token in localStorage
 */
export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('auth_token', token)
  } else {
    localStorage.removeItem('auth_token')
  }
}

