import { useState, useEffect } from 'react'
import api from '../services/api'

export const useVideos = (filters = {}) => {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchVideos()
  }, [filters])

  const fetchVideos = async () => {
    try {
      const response = await api.get('/api/videos', { params: filters })
      setVideos(response.data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const likeVideo = async (videoId) => {
    try {
      const response = await api.post(`/api/videos/${videoId}/like`)
      // Update local state
      setVideos(videos.map(v => 
        v.id === videoId 
          ? { ...v, likes_count: response.data.likes_count, user_likes: response.data.user_likes }
          : v
      ))
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  return { videos, loading, error, refresh: fetchVideos, likeVideo }
}

