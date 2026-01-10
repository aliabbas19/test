import { useState, useEffect } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import StudentManagement from '../components/admin/StudentManagement'
import CriteriaManagement from '../components/admin/CriteriaManagement'
import TelegramSettings from '../components/admin/TelegramSettings'


const AdminDashboard = () => {
  const { isAdmin } = useAuth()
  const [stats, setStats] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [activeTab, setActiveTab] = useState('stats')

  useEffect(() => {
    if (isAdmin) {
      fetchStats()
      if (activeTab === 'metrics') {
        fetchMetrics()
        const interval = setInterval(fetchMetrics, 5000) // Update every 5 seconds
        return () => clearInterval(interval)
      }
    }
  }, [isAdmin, activeTab])

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/admin/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const fetchMetrics = async () => {
    try {
      const response = await api.get('/api/admin/ops/metrics')
      setMetrics(response.data)
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    }
  }

  if (!isAdmin) {
    return <div>ليس لديك صلاحية للوصول</div>
  }

  return (
    <div>
      <div className="bg-white rounded-xl shadow-md border border-gray-200 p-4 mb-8">
        <h1 className="text-3xl lg:text-4xl font-bold text-center text-gray-800">
          <i className="fa-solid fa-gauge-high text-primary ml-2"></i>
          لوحة التحكم الرئيسية
        </h1>
      </div>

      <div className="tabs tabs-boxed mb-8 bg-white p-2 rounded-xl shadow-md border border-gray-200 gap-2">
        <button
          className={`tab tab-lg rounded-lg transition-all font-bold ${activeTab === 'stats'
            ? 'bg-primary text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
          onClick={() => setActiveTab('stats')}
        >
          <i className="fa-solid fa-chart-pie ml-2"></i> الإحصائيات
        </button>
        <button
          className={`tab tab-lg rounded-lg transition-all font-bold ${activeTab === 'criteria'
            ? 'bg-primary text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
          onClick={() => setActiveTab('criteria')}
        >
          <i className="fa-solid fa-list-check ml-2"></i> المعايير
        </button>
        <button
          className={`tab tab-lg rounded-lg transition-all font-bold ${activeTab === 'students'
            ? 'bg-primary text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
          onClick={() => setActiveTab('students')}
        >
          <i className="fa-solid fa-users-gear ml-2"></i> الطلاب
        </button>
        <button
          className={`tab tab-lg rounded-lg transition-all font-bold ${activeTab === 'telegram'
            ? 'bg-primary text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
          onClick={() => setActiveTab('telegram')}
        >
          <i className="fa-brands fa-telegram ml-2"></i> تيليجرام
        </button>
        <button
          className={`tab tab-lg rounded-lg transition-all font-bold ${activeTab === 'metrics'
            ? 'bg-primary text-white shadow-md'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
          onClick={() => setActiveTab('metrics')}
        >
          <i className="fa-solid fa-server ml-2"></i> الخادم
        </button>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-200 min-h-[500px]">
        {activeTab === 'stats' && stats && (
          <div className="space-y-8 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 p-6 rounded-2xl border border-blue-500/20 text-center hover:scale-105 transition-transform">
                <div className="text-blue-500 text-4xl mb-2"><i className="fa-solid fa-users"></i></div>
                <div className="text-gray-500">إجمالي الطلاب</div>
                <div className="text-4xl font-bold text-gray-800">{stats.total_students}</div>
              </div>
              <div className="bg-gradient-to-br from-orange-500/10 to-orange-500/5 p-6 rounded-2xl border border-orange-500/20 text-center hover:scale-105 transition-transform">
                <div className="text-orange-500 text-4xl mb-2"><i className="fa-solid fa-clock"></i></div>
                <div className="text-gray-500">الفيديوهات المعلقة</div>
                <div className="text-4xl font-bold text-gray-800">{stats.pending_videos}</div>
              </div>
              <div className="bg-gradient-to-br from-green-500/10 to-green-500/5 p-6 rounded-2xl border border-green-500/20 text-center hover:scale-105 transition-transform">
                <div className="text-green-500 text-4xl mb-2"><i className="fa-solid fa-envelope"></i></div>
                <div className="text-gray-500">الرسائل غير المقروءة</div>
                <div className="text-4xl font-bold text-gray-800">{stats.unread_messages}</div>
              </div>
            </div>

            <div className="divider"></div>

            <div className="border border-red-200 bg-red-50/50 p-6 rounded-2xl">
              <h2 className="text-xl font-bold text-red-600 mb-2"><i className="fa-solid fa-triangle-exclamation"></i> منطقة الخطر</h2>
              <p className="text-gray-600 mb-4">
                بدء سنة دراسية جديدة سيؤدي إلى حذف جميع البيانات (الفيديوهات، الرسائل، السجلات).
              </p>
              <button
                className="btn btn-error btn-outline gap-2"
                onClick={async () => {
                  if (!confirm('هل أنت متأكد تماماً من رغبتك في بدء سنة دراسية جديدة؟ سيتم حذف جميع البيانات بشكل نهائي!')) {
                    return
                  }
                  if (!confirm('تأكيد نهائي: هل أنت متأكد 100%؟')) {
                    return
                  }
                  try {
                    const response = await api.post('/api/admin/start-new-year')
                    alert(response.data.message || 'تم بدء السنة الدراسية الجديدة بنجاح')
                    window.location.reload()
                  } catch (error) {
                    alert(error.response?.data?.detail || 'حدث خطأ أثناء بدء السنة الجديدة')
                  }
                }}
              >
                <i className="fa-solid fa-skull"></i> بدء سنة جديدة الآن
              </button>
            </div>
          </div>
        )}

        {activeTab === 'students' && <div className="animate-fade-in"><StudentManagement /></div>}
        {activeTab === 'criteria' && <div className="animate-fade-in"><CriteriaManagement /></div>}

        {activeTab === 'telegram' && <TelegramSettings />}


        {activeTab === 'metrics' && metrics && (
          <div className="animate-fade-in grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Metrics cards (simplified for brevity, can enhance later) */}
            <div className="stat bg-white/50 rounded-xl border border-white/20">
              <div className="stat-title">إجمالي الطلبات</div>
              <div className="stat-value text-2xl">{metrics.total_requests || 0}</div>
            </div>
            {/* ... other metrics ... */}
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminDashboard

