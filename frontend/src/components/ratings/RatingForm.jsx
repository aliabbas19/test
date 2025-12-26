import { useState, useEffect } from 'react'
import api from '../../services/api'

const RatingForm = ({ videoId, videoType, onRatingUpdate }) => {
  const [criteria, setCriteria] = useState([])
  const [ratings, setRatings] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

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
    setSaving(true)

    try {
      const response = await api.post(`/api/ratings/video/${videoId}`, {
        video_id: videoId,
        ratings: newRatings
      })

      // Show badge message if awarded
      if (response.data.champion_message) {
        alert(response.data.champion_message)
      }

      // Build ratings array for parent component
      const updatedRatings = criteria.map(c => ({
        id: c.id,
        criterion_id: c.id,
        criterion_name: c.name,
        is_awarded: newRatings[c.key] === 1
      }))

      if (onRatingUpdate) {
        onRatingUpdate({
          ...response.data,
          ratings: updatedRatings
        })
      }
    } catch (error) {
      console.error('Failed to update rating:', error)
    } finally {
      setSaving(false)
    }
  }

  // Calculate stars
  const awardedCount = Object.values(ratings).filter(v => v === 1).length
  const totalCount = criteria.length

  if (loading) {
    return (
      <div className="text-center py-8">
        <span className="loading loading-spinner loading-lg text-warning"></span>
        <p className="mt-2 text-gray-500">جاري تحميل المعايير...</p>
      </div>
    )
  }

  if (criteria.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <i className="fa-solid fa-exclamation-circle text-4xl mb-2 text-warning"></i>
        <p>لا توجد معايير تقييم لهذا النوع من الفيديوهات</p>
        <p className="text-sm mt-1">يرجى إضافة معايير من لوحة التحكم</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Stars Summary */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 p-4 rounded-lg border border-yellow-200">
        <div className="flex items-center justify-between">
          <span className="font-bold text-gray-700">النجوم المكتسبة:</span>
          <div className="flex items-center gap-1">
            {[...Array(totalCount)].map((_, i) => (
              <i
                key={i}
                className={`fa-star ${i < awardedCount ? 'fa-solid text-yellow-500' : 'fa-regular text-gray-300'}`}
              ></i>
            ))}
            <span className="font-bold text-warning mr-2">
              {awardedCount}/{totalCount}
            </span>
          </div>
        </div>
      </div>

      {/* Criteria Checkboxes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {criteria.map((criterion) => (
          <label
            key={criterion.id}
            className={`flex items-center justify-between p-4 rounded-lg border-2 cursor-pointer transition-all ${ratings[criterion.key] === 1
                ? 'bg-yellow-50 border-yellow-400 shadow-sm'
                : 'bg-gray-50 border-gray-200 hover:border-gray-300'
              }`}
          >
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                className="checkbox checkbox-warning checkbox-lg"
                checked={ratings[criterion.key] === 1}
                onChange={(e) => handleChange(criterion.key, e.target.checked)}
                disabled={saving}
              />
              <span className={`font-bold ${ratings[criterion.key] === 1 ? 'text-yellow-700' : 'text-gray-600'}`}>
                {criterion.name}
              </span>
            </div>
            {ratings[criterion.key] === 1 && (
              <i className="fa-solid fa-star text-yellow-500"></i>
            )}
          </label>
        ))}
      </div>

      {saving && (
        <div className="text-center text-sm text-gray-500">
          <span className="loading loading-spinner loading-xs ml-1"></span>
          جاري الحفظ...
        </div>
      )}
    </div>
  )
}

export default RatingForm
