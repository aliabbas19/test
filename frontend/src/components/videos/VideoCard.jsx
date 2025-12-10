import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import VideoPlayer from './VideoPlayer'

const VideoCard = ({ video, onSelect }) => {
  const { isAdmin } = useAuth()
  const [likesCount, setLikesCount] = useState(0)
  const [userLikes, setUserLikes] = useState(false)

  useEffect(() => {
    // Fetch initial like status
    fetchLikeStatus()
  }, [video.id])

  const fetchLikeStatus = async () => {
    try {
      // This would need a GET endpoint to fetch like status
      // For now, we'll get it from the video data if available
    } catch (error) {
      console.error('Failed to fetch like status:', error)
    }
  }

  const handleLike = async () => {
    try {
      const response = await api.post(`/api/videos/${video.id}/like`)
      setLikesCount(response.data.likes_count)
      setUserLikes(response.data.user_likes)
    } catch (error) {
      console.error('Failed to like video:', error)
    }
  }

  return (
    <div className="glass-effect rounded-xl overflow-hidden mb-6 p-1">
      <div className="p-4 border-b border-gray-100/50 flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-800">{video.title}</h2>
        <span className={`badge ${video.video_type === 'اثرائي' ? 'badge-warning' : 'badge-info'}`}>
          {video.video_type}
        </span>
      </div>

      <div className="bg-black/5 p-1 video-container">
        <VideoPlayer src={video.file_url} title={video.title} />
      </div>

      <div className="p-4 flex justify-between items-center bg-white/50">
        <button
          onClick={handleLike}
          className={`btn btn-sm gap-2 ${userLikes ? 'btn-error text-white shadow-lg shadow-red-500/30' : 'btn-ghost text-gray-500 hover:text-red-500 hover:bg-red-50'}`}
        >
          <i className={`${userLikes ? 'fa-solid' : 'fa-regular'} fa-heart text-lg`}></i>
          <span className="font-bold">{likesCount}</span>
        </button>

        <div className="flex gap-2">
          {isAdmin && !video.is_approved && (
            <button
              onClick={async () => {
                await api.post(`/api/videos/${video.id}/approve`)
                if (onSelect) onSelect()
              }}
              className="btn btn-sm btn-success text-white"
            >
              <i className="fa-solid fa-check mr-1"></i> موافقة
            </button>
          )}
          <button
            onClick={() => onSelect && onSelect(video)}
            className="btn btn-sm btn-primary btn-outline gap-2"
          >
            عرض التفاصيل <i className="fa-solid fa-arrow-left"></i>
          </button>
        </div>
      </div>
    </div>
  )
}

export default VideoCard

