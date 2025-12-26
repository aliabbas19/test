import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import VideoPlayer from './VideoPlayer'
import CommentSection from '../comments/CommentSection'
import RatingForm from '../ratings/RatingForm'

const VideoCard = ({ video, onApprove, onDelete, onUpdate }) => {
  const { user, isAdmin } = useAuth()
  // Initialize from video data (comes from API)
  const [likesCount, setLikesCount] = useState(video.likes_count || 0)
  const [userLikes, setUserLikes] = useState(video.user_likes || false)
  const [deleting, setDeleting] = useState(false)
  const [videoTitle, setVideoTitle] = useState(video.title)
  const [videoType, setVideoType] = useState(video.video_type)
  const [ratings, setRatings] = useState(video.ratings || [])

  // Edit modal state
  const [showEditModal, setShowEditModal] = useState(false)
  const [editTitle, setEditTitle] = useState(video.title)
  const [editType, setEditType] = useState(video.video_type)
  const [saving, setSaving] = useState(false)

  // Rating modal state
  const [showRatingModal, setShowRatingModal] = useState(false)

  // Check if current user is the owner
  const isOwner = user?.id === video.user_id

  // Calculate awarded stars count
  const awardedStars = ratings.filter(r => r.is_awarded).length

  // Update state when video prop changes
  useEffect(() => {
    setLikesCount(video.likes_count || 0)
    setUserLikes(video.user_likes || false)
    setVideoTitle(video.title)
    setVideoType(video.video_type)
    setRatings(video.ratings || [])
  }, [video.id, video.likes_count, video.user_likes, video.title, video.video_type, video.ratings])

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

  const handleDelete = async () => {
    if (!confirm('هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا الإجراء.')) return

    setDeleting(true)
    try {
      await api.delete(`/api/videos/${video.id}`)
      if (onDelete) onDelete(video.id)
      alert('تم حذف الفيديو بنجاح')
    } catch (error) {
      console.error('Failed to delete video:', error)
      alert('حدث خطأ أثناء حذف الفيديو')
    } finally {
      setDeleting(false)
    }
  }

  const handleEdit = () => {
    setEditTitle(videoTitle)
    setEditType(videoType)
    setShowEditModal(true)
  }

  const handleSaveEdit = async () => {
    setSaving(true)
    try {
      const response = await api.put(`/api/videos/${video.id}`, null, {
        params: {
          title: editTitle,
          video_type: editType
        }
      })
      setVideoTitle(response.data.video.title)
      setVideoType(response.data.video.video_type)
      setShowEditModal(false)
      alert('تم تحديث الفيديو بنجاح')
      if (onUpdate) onUpdate(video.id, response.data.video)
    } catch (error) {
      console.error('Failed to update video:', error)
      alert(error.response?.data?.detail || 'حدث خطأ أثناء تحديث الفيديو')
    } finally {
      setSaving(false)
    }
  }

  const handleRatingUpdate = (updatedData) => {
    // Refresh ratings after update
    if (updatedData && updatedData.ratings) {
      setRatings(updatedData.ratings)
    }
    // Also trigger parent refresh if available
    if (onUpdate) onUpdate(video.id, { ...video, ratings: updatedData?.ratings })
  }

  return (
    <>
      <div className="bg-white rounded-xl overflow-hidden mb-6 shadow-md border border-gray-100">
        {/* Video Header */}
        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <h2 className="text-lg font-bold text-gray-800">{videoTitle}</h2>
          <div className="flex items-center gap-2">
            {/* Stars count badge */}
            {awardedStars > 0 && (
              <span className="badge badge-warning gap-1 text-white">
                <i className="fa-solid fa-star"></i>
                {awardedStars}
              </span>
            )}
            <span className={`badge ${videoType === 'اثرائي' ? 'badge-warning' : 'badge-info'} text-white`}>
              {videoType}
            </span>
          </div>
        </div>

        {/* Video Player */}
        <div className="bg-black">
          <VideoPlayer
            src={video.file_url || (video.filepath ? `/data/uploads/${video.filepath}` : '')}
            title={videoTitle}
          />
        </div>

        {/* Ratings Display */}
        {ratings && ratings.length > 0 && (
          <div className="p-3 bg-gray-50 border-b border-gray-100">
            <div className="flex flex-wrap gap-2">
              {ratings.map((rating) => (
                <div
                  key={rating.id}
                  className={`badge gap-1 p-3 ${rating.is_awarded ? 'badge-warning text-white shadow-sm' : 'badge-ghost opacity-50'}`}
                >
                  {rating.is_awarded ? (
                    <i className="fa-solid fa-star text-yellow-100"></i>
                  ) : (
                    <i className="fa-regular fa-star"></i>
                  )}
                  <span className="font-bold">{rating.criterion_name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions Bar */}
        <div className="p-3 flex justify-between items-center bg-white border-b border-gray-100">
          <div className="flex gap-2">
            <button
              onClick={handleLike}
              className={`btn btn-sm gap-2 ${userLikes
                ? 'btn-error text-white shadow-sm'
                : 'btn-ghost text-gray-500 hover:text-red-500 hover:bg-red-50'}`}
            >
              <i className={`${userLikes ? 'fa-solid' : 'fa-regular'} fa-heart text-lg`}></i>
              <span className="font-bold">{likesCount}</span>
            </button>
          </div>

          <div className="flex gap-2">
            {/* Admin Rating Button */}
            {isAdmin && video.is_approved && (
              <button
                onClick={() => setShowRatingModal(true)}
                className="btn btn-sm btn-warning text-white gap-1"
              >
                <i className="fa-solid fa-star"></i> تقييم
              </button>
            )}

            {/* Admin Edit Button */}
            {isAdmin && (
              <button
                onClick={handleEdit}
                className="btn btn-sm btn-info text-white gap-1"
              >
                <i className="fa-solid fa-pen"></i> تعديل
              </button>
            )}

            {/* Admin Approve Button */}
            {isAdmin && !video.is_approved && (
              <button
                onClick={handleApprove}
                className="btn btn-sm btn-success text-white gap-1"
              >
                <i className="fa-solid fa-check"></i> موافقة
              </button>
            )}

            {/* Delete Button - for owner or admin */}
            {(isOwner || isAdmin) && (
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="btn btn-sm btn-error text-white gap-1"
              >
                {deleting ? (
                  <span className="loading loading-spinner loading-xs"></span>
                ) : (
                  <i className="fa-solid fa-trash"></i>
                )}
                حذف
              </button>
            )}
          </div>
        </div>

        {/* Inline Instagram-style Comments */}
        <div className="border-t border-gray-100 bg-white">
          <CommentSection videoId={video.id} compact={true} />
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white p-6 rounded-xl w-full max-w-md shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-800">
                <i className="fa-solid fa-pen-to-square text-info ml-2"></i>
                تعديل الفيديو
              </h3>
              <button
                onClick={() => setShowEditModal(false)}
                className="btn btn-sm btn-circle btn-ghost"
              >
                <i className="fa-solid fa-xmark"></i>
              </button>
            </div>

            <div className="space-y-4">
              {/* Title Input */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-bold">عنوان الفيديو</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  placeholder="أدخل عنوان الفيديو"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                />
              </div>

              {/* Video Type Select */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-bold">نوع الفيديو</span>
                </label>
                <select
                  className="select select-bordered w-full"
                  value={editType}
                  onChange={(e) => setEditType(e.target.value)}
                >
                  <option value="منهجي">منهجي</option>
                  <option value="اثرائي">اثرائي</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={handleSaveEdit}
                disabled={saving || !editTitle.trim()}
                className="btn btn-primary flex-1"
              >
                {saving ? (
                  <span className="loading loading-spinner"></span>
                ) : (
                  <>
                    <i className="fa-solid fa-check ml-1"></i> حفظ
                  </>
                )}
              </button>
              <button
                onClick={() => setShowEditModal(false)}
                className="btn btn-ghost"
              >
                إلغاء
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Rating Modal */}
      {showRatingModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white p-6 rounded-xl w-full max-w-lg shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-800">
                <i className="fa-solid fa-star text-warning ml-2"></i>
                تقييم الفيديو
              </h3>
              <button
                onClick={() => setShowRatingModal(false)}
                className="btn btn-sm btn-circle btn-ghost"
              >
                <i className="fa-solid fa-xmark"></i>
              </button>
            </div>

            <RatingForm
              videoId={video.id}
              videoType={videoType}
              onRatingUpdate={handleRatingUpdate}
            />

            <div className="flex justify-end mt-4">
              <button
                onClick={() => setShowRatingModal(false)}
                className="btn btn-primary"
              >
                <i className="fa-solid fa-check ml-1"></i> تم
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default VideoCard
