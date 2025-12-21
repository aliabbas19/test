import { useState, useEffect } from 'react'
import api from '../services/api'
import VideoCard from '../components/videos/VideoCard'

const Archive = () => {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchVideos()
  }, [])

  const fetchVideos = async () => {
    try {
      const response = await api.get('/api/videos', {
        params: { is_archived: true },
      })
      setVideos(response.data)
    } catch (error) {
      console.error('Failed to fetch archived videos:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    )
  }

  return (
    <div>
      <div className="ship-frame text-2xl lg:text-3xl mb-8 mx-auto w-fit">
        <span className="animate-text-gradient bg-gradient-to-r from-blue-600 via-primary to-blue-600 bg-[length:200%_auto] bg-clip-text text-transparent">
          الأرشيف
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos.map((video) => (
          <VideoCard
            key={video.id}
            video={video}
            onDelete={(videoId) => setVideos(videos.filter(v => v.id !== videoId))}
          />
        ))}
      </div>
      {videos.length === 0 && (
        <div className="glass-effect p-12 rounded-xl text-center">
          <i className="fa-solid fa-box-archive text-6xl text-gray-300 mb-4 block"></i>
          <p className="text-gray-500 text-lg">لا توجد فيديوهات في الأرشيف</p>
        </div>
      )}
    </div>
  )
}

export default Archive

