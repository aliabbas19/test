import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useAuth } from '../../context/AuthContext'

const VideoReview = ({ video, onUpdate }) => {
  const { isAdmin } = useAuth()
  const [ratings, setRatings] = useState({})
  const [criteria, setCriteria] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isAdmin && video) {
      fetchCriteria()
      fetchRatings()
    }
  }, [video, isAdmin])

  const fetchCriteria = async () => {
    try {
      const response = await api.get('/api/ratings/criteria', {
        params: { video_type: video.video_type }
      })
      setCriteria(response.data)
    } catch (error) {
      console.error('Failed to fetch criteria:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRatings = async () => {
    try {
      const response = await api.get(`/api/ratings/video/${video.id}`)
      setRatings(response.data.ratings || {})
    } catch (error) {
      console.error('Failed to fetch ratings:', error)
    }
  }

  const handleRatingChange = async (criterionKey, value) => {
    const newRatings = { ...ratings, [criterionKey]: value ? 1 : 0 }
    setRatings(newRatings)

    try {
      await api.post(`/api/ratings/video/${video.id}`, {
        video_id: video.id,
        ratings: newRatings
      })
      if (onUpdate) onUpdate()
    } catch (error) {
      console.error('Failed to update rating:', error)
    }
  }

  if (!isAdmin || loading) return null

  return (
    <div className="card bg-base-200 p-4 mt-4">
      <h3 className="font-bold mb-2">تقييم الفيديو ({video.video_type})</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {criteria.map((criterion) => (
          <label key={criterion.id} className="label cursor-pointer">
            <span className="label-text">{criterion.name}</span>
            <input
              type="checkbox"
              className="checkbox checkbox-primary"
              checked={ratings[criterion.key] === 1}
              onChange={(e) => handleRatingChange(criterion.key, e.target.checked)}
            />
          </label>
        ))}
      </div>
    </div>
  )
}

export default VideoReview

