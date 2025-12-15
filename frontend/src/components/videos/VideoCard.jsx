import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import VideoPlayer from './VideoPlayer'
import CommentSection from '../comments/CommentSection'

const VideoCard = ({ video, onApprove }) => {
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

  const handleApprove = async () => {
    try {
      await api.post(`/api/videos/${video.id}/approve`)
      if (onApprove) onApprove()
    } catch (error) {
      console.error('Failed to approve video:', error)
    }
  }

  return (
    <div className="bg-white rounded-xl overflow-hidden mb-6 shadow-md border border-gray-100">
      {/* Video Header */}
      <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
        <h2 className="text-lg font-bold text-gray-800">{video.title}</h2>
        <span className={`badge ${video.video_type === 'اثرائي' ? 'badge-warning' : 'badge-info'} text-white`}>
          {video.video_type}
        </span>
      </div>

      {/* Video Player */}
      <div className="bg-black">
        <VideoPlayer
          src={video.file_url || (video.filepath ? `/data/uploads/${video.filepath}` : '')}
          title={video.title}
        />
      </div>

      {/* Actions Bar */}
      <div className="p-3 flex justify-between items-center bg-white border-b border-gray-100">
        <button
          onClick={handleLike}
          className={`btn btn-sm gap-2 ${userLikes
            ? 'btn-error text-white shadow-sm'
            : 'btn-ghost text-gray-500 hover:text-red-500 hover:bg-red-50'}`}
        >
          <i className={`${userLikes ? 'fa-solid' : 'fa-regular'} fa-heart text-lg`}></i>
          <span className="font-bold">{likesCount}</span>
        </button>

        {/* Admin Approve Button */}
        {isAdmin && !video.is_approved && (
          <button
            onClick={handleApprove}
            className="btn btn-sm btn-success text-white gap-1"
          >
            <i className="fa-solid fa-check"></i> موافقة
          </button>
        )}
      </div>

      {/* Inline Instagram-style Comments */}
      <div className="border-t border-gray-100 bg-white">
        <CommentSection videoId={video.id} compact={true} />
      </div>
    </div>
  )
}

export default VideoCard


