import api from './api'

/**
 * Upload file to S3 via backend
 * @param {File} file - File to upload
 * @param {string} type - 'video' or 'profile-image'
 * @param {object} additionalData - Additional form data
 * @param {function} onProgress - Progress callback
 * @returns {Promise} Upload result
 */
export const uploadFile = async (file, type, additionalData = {}, onProgress = null) => {
  const formData = new FormData()
  formData.append(type === 'video' ? 'video_file' : 'image_file', file)
  
  // Add additional data
  Object.keys(additionalData).forEach(key => {
    formData.append(key, additionalData[key])
  })

  const config = {
    headers: { 'Content-Type': 'multipart/form-data' }
  }

  if (onProgress) {
    config.onUploadProgress = (progressEvent) => {
      const percentCompleted = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      )
      onProgress(percentCompleted)
    }
  }

  const endpoint = type === 'video' 
    ? '/api/uploads/video' 
    : '/api/uploads/profile-image'

  const response = await api.post(endpoint, formData, config)
  return response.data
}

/**
 * Get file URL from S3 key
 * @param {string} s3Key - S3 object key
 * @returns {string} File URL
 */
export const getFileUrl = (s3Key) => {
  // In production, this would use CloudFront signed URLs
  // For now, return a presigned URL from backend
  return `/api/uploads/file/${encodeURIComponent(s3Key)}`
}

