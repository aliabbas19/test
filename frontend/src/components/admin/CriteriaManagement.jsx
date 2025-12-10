import { useState, useEffect } from 'react'
import api from '../../services/api'

const CriteriaManagement = () => {
  const [criteria, setCriteria] = useState([])
  const [loading, setLoading] = useState(true)
  const [newCriterion, setNewCriterion] = useState({
    name: '',
    key: '',
    video_type: 'منهجي'
  })

  useEffect(() => {
    fetchCriteria()
  }, [])

  const fetchCriteria = async () => {
    try {
      const response = await api.get('/api/ratings/criteria')
      setCriteria(response.data)
    } catch (error) {
      console.error('Failed to fetch criteria:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/api/ratings/criteria', newCriterion)
      setNewCriterion({ name: '', key: '', video_type: 'منهجي' })
      fetchCriteria()
    } catch (error) {
      console.error('Failed to create criterion:', error)
      alert('فشل إنشاء المعيار. تأكد من أن المفتاح فريد.')
    }
  }

  const handleDelete = async (criterionId) => {
    if (!confirm('هل أنت متأكد من حذف هذا المعيار؟')) return

    try {
      await api.delete(`/api/ratings/criteria/${criterionId}`)
      fetchCriteria()
    } catch (error) {
      console.error('Failed to delete criterion:', error)
    }
  }

  const groupedCriteria = {
    'منهجي': criteria.filter(c => c.video_type === 'منهجي'),
    'اثرائي': criteria.filter(c => c.video_type === 'اثرائي')
  }

  if (loading) {
    return <div className="text-center py-4">جاري التحميل...</div>
  }

  return (
    <div>
      <div className="glass-effect p-6 rounded-xl mb-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <i className="fa-solid fa-plus-circle text-primary"></i> إضافة معيار جديد
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              className="input input-bordered bg-white/50 w-full"
              placeholder="اسم المعيار (مثلاً: الحفظ)"
              value={newCriterion.name}
              onChange={(e) => setNewCriterion({ ...newCriterion, name: e.target.value })}
              required
            />
            <input
              type="text"
              className="input input-bordered bg-white/50 w-full"
              placeholder="المفتاح الفريد (key)"
              value={newCriterion.key}
              onChange={(e) => setNewCriterion({ ...newCriterion, key: e.target.value })}
              required
            />
            <select
              className="select select-bordered bg-white/50 w-full"
              value={newCriterion.video_type}
              onChange={(e) => setNewCriterion({ ...newCriterion, video_type: e.target.value })}
              required
            >
              <option value="منهجي">منهجي</option>
              <option value="اثرائي">اثرائي</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary mt-4 text-white font-bold px-8 shadow-lg">
            <i className="fa-solid fa-save ml-2"></i> إضافة المعيار
          </button>
        </form>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {['منهجي', 'اثرائي'].map((type) => (
          <div key={type} className="glass-effect p-6 rounded-xl relative overflow-hidden group hover:border-primary/30 transition-all duration-300">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-20"></div>
            <h3 className="text-lg font-bold mb-4 border-b border-gray-200 pb-2 flex justify-between items-center">
              <span>معايير {type}</span>
              <span className="badge badge-primary badge-outline">{groupedCriteria[type].length}</span>
            </h3>
            <div className="space-y-3">
              {groupedCriteria[type].map((criterion) => (
                <div key={criterion.id} className="flex justify-between items-center p-3 bg-white/40 rounded-lg border border-white/40 hover:bg-white/60 transition-colors">
                  <div>
                    <p className="font-bold text-gray-800">{criterion.name}</p>
                    <p className="text-xs text-gray-500 font-mono bg-gray-100 px-1 rounded inline-block">k: {criterion.key}</p>
                  </div>
                  <button
                    onClick={() => handleDelete(criterion.id)}
                    className="btn btn-ghost btn-sm text-error hover:bg-error/10"
                    title="حذف"
                  >
                    <i className="fa-solid fa-trash-can"></i>
                  </button>
                </div>
              ))}
              {groupedCriteria[type].length === 0 && (
                <p className="text-gray-400 text-center py-4 text-sm">لا توجد معايير مضافة</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default CriteriaManagement

