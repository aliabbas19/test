import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import ProfileImage from '../common/ProfileImage'

const CommentSection = ({ videoId }) => {
  const { user, isAdmin } = useAuth()
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchComments()
  }, [videoId])

  const fetchComments = async () => {
    try {
      const response = await api.get(`/api/comments/video/${videoId}`)
      setComments(response.data)
    } catch (error) {
      console.error('Failed to fetch comments:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!newComment.trim()) return

    try {
      await api.post('/api/comments', {
        video_id: videoId,
        content: newComment
      })
      setNewComment('')
      fetchComments()
    } catch (error) {
      console.error('Failed to post comment:', error)
    }
  }

  const handleDelete = async (commentId) => {
    if (!confirm('هل أنت متأكد من حذف هذا التعليق؟')) return

    try {
      await api.delete(`/api/comments/${commentId}`)
      fetchComments()
    } catch (error) {
      console.error('Failed to delete comment:', error)
    }
  }

  const handlePin = async (commentId) => {
    try {
      await api.post(`/api/comments/${commentId}/pin`)
      fetchComments()
    } catch (error) {
      console.error('Failed to pin comment:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-4">جاري التحميل...</div>
  }

  return (
    <div className="mt-4">
      <h3 className="font-bold mb-2">التعليقات ({comments.length})</h3>
      
      <div className="space-y-2 mb-4">
        {comments.map((comment) => (
          <div
            key={comment.id}
            className={`p-3 rounded ${
              comment.is_pinned ? 'bg-warning bg-opacity-25' : 'bg-base-200'
            }`}
          >
            <div className="flex items-start gap-2">
              <ProfileImage src={comment.user?.profile_image} size="sm" />
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <span className="font-bold">
                    {comment.is_pinned && '📌 '}
                    {comment.user?.full_name || comment.user?.username}
                  </span>
                  <div className="flex gap-2">
                    {isAdmin && (
                      <button
                        onClick={() => handlePin(comment.id)}
                        className="btn btn-xs btn-ghost"
                      >
                        📌
                      </button>
                    )}
                    {(user?.id === comment.user_id || isAdmin) && (
                      <button
                        onClick={() => handleDelete(comment.id)}
                        className="btn btn-xs btn-error"
                      >
                        حذف
                      </button>
                    )}
                  </div>
                </div>
                <p className="text-sm mt-1">{comment.content}</p>
                <span className="text-xs text-gray-500">
                  {new Date(comment.timestamp).toLocaleString('ar-EG')}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          className="input input-bordered flex-1"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="اكتب تعليقاً..."
        />
        <button type="submit" className="btn btn-primary">
          إرسال
        </button>
      </form>
    </div>
  )
}

export default CommentSection

