import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import ProfileImage from '../common/ProfileImage'

const CommentSection = ({ videoId, compact = false }) => {
  const { user, isAdmin } = useAuth()
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [loading, setLoading] = useState(true)
  const [showAllComments, setShowAllComments] = useState(false)

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
    return <div className="text-center py-4"><span className="loading loading-spinner loading-sm"></span></div>
  }

  // In compact mode, show only last 2 comments unless expanded
  const displayComments = compact && !showAllComments
    ? comments.slice(-2)
    : comments

  return (
    <div className={compact ? "p-3" : "mt-4 p-4"}>
      {!compact && <h3 className="font-bold mb-2 text-gray-800">التعليقات ({comments.length})</h3>}

      <div className="space-y-2 mb-3">
        {/* Show all comments button in compact mode */}
        {compact && comments.length > 2 && !showAllComments && (
          <button
            onClick={() => setShowAllComments(true)}
            className="text-sm text-gray-500 hover:text-primary transition-colors"
          >
            عرض جميع التعليقات ({comments.length})
          </button>
        )}

        {displayComments.map((comment) => (
          <div
            key={comment.id}
            className={`p-2 rounded-lg ${comment.is_pinned ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'
              }`}
          >
            <div className="flex items-start gap-2">
              <ProfileImage src={comment.user?.profile_image} size="sm" />
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-sm text-gray-800">
                    {comment.is_pinned && '📌 '}
                    {comment.user?.full_name || comment.user?.username}
                  </span>
                  <div className="flex gap-1">
                    {isAdmin && (
                      <button
                        onClick={() => handlePin(comment.id)}
                        className="btn btn-xs btn-ghost text-gray-400 hover:text-yellow-500"
                        title="تثبيت"
                      >
                        📌
                      </button>
                    )}
                    {(user?.id === comment.user_id || isAdmin) && (
                      <button
                        onClick={() => handleDelete(comment.id)}
                        className="btn btn-xs btn-ghost text-gray-400 hover:text-red-500"
                        title="حذف"
                      >
                        <i className="fa-solid fa-trash-can text-xs"></i>
                      </button>
                    )}
                  </div>
                </div>
                <p className="text-sm mt-1 text-gray-700">{comment.content}</p>
                <span className="text-xs text-gray-400">
                  {new Date(comment.timestamp).toLocaleString('ar-EG')}
                </span>
              </div>
            </div>
          </div>
        ))}

        {comments.length === 0 && (
          <p className="text-sm text-gray-400 text-center py-2">لا توجد تعليقات بعد</p>
        )}
      </div>

      {/* Instagram-style comment input */}
      <form onSubmit={handleSubmit} className="flex gap-2 items-center border-t border-gray-100 pt-3">
        <input
          type="text"
          className={`input ${compact ? 'input-sm' : ''} input-bordered flex-1 bg-white text-gray-800 border-gray-200 focus:border-primary`}
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="اكتب تعليقاً..."
        />
        <button
          type="submit"
          className={`btn ${compact ? 'btn-sm' : ''} btn-primary text-white`}
          disabled={!newComment.trim()}
        >
          <i className="fa-solid fa-paper-plane"></i>
        </button>
      </form>
    </div>
  )
}

export default CommentSection


