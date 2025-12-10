import { useState, useEffect } from 'react'
import api from '../../services/api'

const RatingForm = ({ videoId, videoType, onRatingUpdate }) => {
  const [criteria, setCriteria] = useState([])
  const [ratings, setRatings] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCriteria()
    fetchCurrentRatings()
  }, [videoId, videoType])

  const fetchCriteria = async () => {
    try {
      const response = await api.get('/api/ratings/criteria', {
        params: { video_type: videoType }
      })
      setCriteria(response.data)
    } catch (error) {
      console.error('Failed to fetch criteria:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCurrentRatings = async () => {
    try {
      const response = await api.get(`/api/ratings/video/${videoId}`)
      setRatings(response.data.ratings || {})
    } catch (error) {
      console.error('Failed to fetch ratings:', error)
    }
  }

  const handleChange = async (criterionKey, checked) => {
    const newRatings = { ...ratings, [criterionKey]: checked ? 1 : 0 }
    setRatings(newRatings)

    try {
      const response = await api.post(`/api/ratings/video/${videoId}`, {
        video_id: videoId,
        ratings: newRatings
      })
      if (onRatingUpdate) onRatingUpdate(response.data)
    } catch (error) {
      console.error('Failed to update rating:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-4">جاري التحميل...</div>
  }

  return (
    <div className="card bg-base-200 p-4">
      <h3 className="font-bold mb-3">معايير التقييم ({videoType})</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {criteria.map((criterion) => (
          <label key={criterion.id} className="label cursor-pointer">
            <span className="label-text">{criterion.name}</span>
            <input
              type="checkbox"
              className="checkbox checkbox-primary"
              checked={ratings[criterion.key] === 1}
              onChange={(e) => handleChange(criterion.key, e.target.checked)}
            />
          </label>
        ))}
      </div>
    </div>
  )
}

export default RatingForm

