import { useState, useEffect } from 'react'
import api from '../../services/api'
import ProfileImage from '../common/ProfileImage'

const StudentManagement = () => {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    class_name: '',
    section_name: '',
    search_name: ''
  })

  useEffect(() => {
    fetchStudents()
  }, [filters])

  const fetchStudents = async () => {
    try {
      const params = { role: 'student', ...filters }
      const response = await api.get('/api/users', { params })
      setStudents(response.data)
    } catch (error) {
      console.error('Failed to fetch students:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSuspend = async (studentId, days, reason) => {
    if (!confirm(`هل أنت متأكد من تعليق هذا الطالب لمدة ${days} يوم؟`)) return

    try {
      await api.post(`/api/admin/users/${studentId}/suspend?days=${days}&reason=${encodeURIComponent(reason || 'لا يوجد سبب')}`)
      alert('تم تعليق الطالب بنجاح')
      fetchStudents()
    } catch (error) {
      console.error('Failed to suspend student:', error)
      alert(error.response?.data?.detail || 'فشل تعليق الطالب')
    }
  }

  const handleKick = async (studentId) => {
    if (!confirm('هل أنت متأكد من طرد هذا الطالب؟')) return

    try {
      await api.post(`/api/admin/users/${studentId}/kick`)
      alert('تم طرد الطالب بنجاح')
      fetchStudents()
    } catch (error) {
      console.error('Failed to kick student:', error)
      alert(error.response?.data?.detail || 'فشل طرد الطالب')
    }
  }

  const handleMute = async (studentId) => {
    try {
      await api.post(`/api/admin/users/${studentId}/mute`)
      alert('تم تحديث حالة الكتم بنجاح')
      fetchStudents()
    } catch (error) {
      console.error('Failed to mute student:', error)
      alert(error.response?.data?.detail || 'فشل تحديث حالة الكتم')
    }
  }

  const handleLiftSuspension = async (studentId) => {
    if (!confirm('هل أنت متأكد من رفع الإيقاف عن هذا الطالب؟')) return

    try {
      await api.post(`/api/admin/users/${studentId}/lift-suspension`)
      alert('تم رفع الإيقاف بنجاح')
      fetchStudents()
    } catch (error) {
      console.error('Failed to lift suspension:', error)
      alert(error.response?.data?.detail || 'فشل رفع الإيقاف')
    }
  }

  const handleUnbindDevice = async (studentId) => {
    if (!confirm('هل أنت متأكد من إلغاء ربط الجهاز لهذا الطالب؟')) return

    try {
      await api.post(`/api/admin/users/${studentId}/unbind-device`)
      alert('تم إلغاء ربط الجهاز بنجاح')
      fetchStudents()
    } catch (error) {
      console.error('Failed to unbind device:', error)
      alert(error.response?.data?.detail || 'فشل إلغاء ربط الجهاز')
    }
  }

  const handleRevokeSessions = async (studentId) => {
    if (!confirm('هل أنت متأكد من إبطال جميع جلسات هذا الطالب؟')) return

    try {
      await api.post(`/api/admin/users/${studentId}/revoke-sessions`)
      alert('تم إبطال جميع الجلسات بنجاح')
      fetchStudents()
    } catch (error) {
      console.error('Failed to revoke sessions:', error)
      alert(error.response?.data?.detail || 'فشل إبطال الجلسات')
    }
  }

  const handleDelete = async (studentId) => {
    if (!confirm('هل أنت متأكد من حذف هذا الطالب؟ هذا الإجراء لا يمكن التراجع عنه!')) return

    try {
      await api.delete(`/api/admin/users/${studentId}`)
      alert('تم حذف الطالب بنجاح')
      fetchStudents()
    } catch (error) {
      console.error('Failed to delete student:', error)
      alert(error.response?.data?.detail || 'فشل حذف الطالب')
    }
  }

  if (loading) {
    return <div className="text-center py-4">جاري التحميل...</div>
  }

  return (
    <div>
      <div className="glass-effect p-6 rounded-xl mb-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <i className="fa-solid fa-filter text-primary"></i> فلترة الطلاب
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            className="input input-bordered bg-white/50 w-full"
            placeholder="البحث بالاسم..."
            value={filters.search_name}
            onChange={(e) => setFilters({ ...filters, search_name: e.target.value })}
          />
          <input
            type="text"
            className="input input-bordered bg-white/50 w-full"
            placeholder="الصف..."
            value={filters.class_name}
            onChange={(e) => setFilters({ ...filters, class_name: e.target.value })}
          />
          <input
            type="text"
            className="input input-bordered bg-white/50 w-full"
            placeholder="الشعبة..."
            value={filters.section_name}
            onChange={(e) => setFilters({ ...filters, section_name: e.target.value })}
          />
        </div>
      </div>

      <div className="glass-effect rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead className="bg-primary/10 text-primary font-bold text-lg">
              <tr>
                <th>الاسم</th>
                <th>الصف / الشعبة</th>
                <th>الحالة</th>
                <th className="text-center">إجراءات</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id} className="hover:bg-white/30 transition-colors border-b border-primary/5">
                  <td>
                    <div className="flex items-center gap-3">
                      <ProfileImage src={student.profile_image} size="md" />
                      <div>
                        <div className="font-bold">{student.full_name || student.username}</div>
                        <div className="text-sm opacity-50">{student.username}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-ghost badge-sm">{student.class_name} - {student.section_name}</span>
                  </td>
                  <td>
                    {student.is_suspended ? (
                      <span className="badge badge-error gap-1"><i className="fa-solid fa-ban"></i> موقوف</span>
                    ) : (
                      <span className="badge badge-success gap-1"><i className="fa-solid fa-check"></i> نشط</span>
                    )}
                  </td>
                  <td className="text-center">
                    <div className="join shadow-sm">
                      <button
                        onClick={() => handleUnbindDevice(student.id)}
                        className="btn btn-sm btn-warning join-item tooltip"
                        data-tip="فك ربط الجهاز"
                      >
                        <i className="fa-solid fa-mobile-screen-button"></i>
                      </button>
                      <div className="dropdown dropdown-left join-item">
                        <label tabIndex={0} className="btn btn-sm btn-info rounded-none">
                          <i className="fa-solid fa-gavel"></i>
                        </label>
                        <ul tabIndex={0} className="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 z-50">
                          <li><a onClick={() => handleSuspend(student.id, 1, 'مخالفة بسيطة')}>تعليق يوم</a></li>
                          <li><a onClick={() => handleSuspend(student.id, 7, 'مخالفة متوسطة')}>تعليق أسبوع</a></li>
                          <li><a onClick={() => handleLiftSuspension(student.id)}>رفع الإيقاف</a></li>
                          <li><a onClick={() => handleKick(student.id)} className="text-error">طرد</a></li>
                        </ul>
                      </div>
                      <button
                        onClick={() => handleDelete(student.id)}
                        className="btn btn-sm btn-error join-item tooltip"
                        data-tip="حذف الطالب"
                      >
                        <i className="fa-solid fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {students.length === 0 && (
          <div className="text-center py-12">
            <i className="fa-solid fa-users-slash text-6xl text-gray-300 mb-4"></i>
            <p className="text-gray-500">لا يوجد طلاب مطابقين للبحث</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default StudentManagement

