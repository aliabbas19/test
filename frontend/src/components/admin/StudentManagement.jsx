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

  // حالة إضافة طالب جديد
  const [showAddModal, setShowAddModal] = useState(false)
  const [newStudent, setNewStudent] = useState({
    username: '',
    password: '',
    full_name: '',
    class_name: '',
    section_name: '',
    role: 'student'
  })
  const [addingStudent, setAddingStudent] = useState(false)

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

  const handleAddStudent = async (e) => {
    e.preventDefault()

    if (!newStudent.username || !newStudent.password) {
      alert('يرجى إدخال اسم المستخدم وكلمة المرور')
      return
    }

    setAddingStudent(true)
    try {
      await api.post('/api/admin/users', newStudent)
      alert('تم إضافة الطالب بنجاح')
      setShowAddModal(false)
      setNewStudent({
        username: '',
        password: '',
        full_name: '',
        class_name: '',
        section_name: '',
        role: 'student'
      })
      fetchStudents()
    } catch (error) {
      console.error('Failed to add student:', error)
      alert(error.response?.data?.detail || 'فشل إضافة الطالب')
    } finally {
      setAddingStudent(false)
    }
  }

  if (loading) {
    return <div className="text-center py-4">جاري التحميل...</div>
  }

  return (
    <div>
      {/* زر إضافة مستخدم جديد */}
      <div className="glass-effect p-4 md:p-6 rounded-xl mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <h2 className="text-lg md:text-xl font-bold flex items-center gap-2">
            <i className="fa-solid fa-user-plus text-primary"></i> إضافة مستخدم
          </h2>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => {
                setNewStudent({ ...newStudent, role: 'student' })
                setShowAddModal(true)
              }}
              className="btn btn-primary btn-sm md:btn-md gap-2"
            >
              <i className="fa-solid fa-user-graduate"></i> إضافة طالب
            </button>
            <button
              onClick={() => {
                setNewStudent({ ...newStudent, role: 'admin' })
                setShowAddModal(true)
              }}
              className="btn btn-secondary btn-sm md:btn-md gap-2"
            >
              <i className="fa-solid fa-user-shield"></i> إضافة أدمن
            </button>
          </div>
        </div>
      </div>

      {/* Modal إضافة طالب */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="glass-effect p-6 rounded-xl w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">
                <i className={`fa-solid ${newStudent.role === 'admin' ? 'fa-user-shield text-secondary' : 'fa-user-graduate text-primary'} ml-2`}></i>
                إضافة {newStudent.role === 'admin' ? 'أدمن' : 'طالب'} جديد
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="btn btn-sm btn-circle btn-ghost"
              >
                <i className="fa-solid fa-xmark"></i>
              </button>
            </div>

            <form onSubmit={handleAddStudent} className="space-y-4">
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-bold">اسم المستخدم (الرمز) *</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  placeholder="مثال: student123"
                  value={newStudent.username}
                  onChange={(e) => setNewStudent({ ...newStudent, username: e.target.value })}
                  required
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-bold">كلمة المرور *</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  placeholder="كلمة المرور"
                  value={newStudent.password}
                  onChange={(e) => setNewStudent({ ...newStudent, password: e.target.value })}
                  required
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-bold">الاسم الكامل</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  placeholder="اسم الطالب"
                  value={newStudent.full_name}
                  onChange={(e) => setNewStudent({ ...newStudent, full_name: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-bold">الصف</span>
                  </label>
                  <select
                    className="select select-bordered w-full"
                    value={newStudent.class_name}
                    onChange={(e) => setNewStudent({ ...newStudent, class_name: e.target.value })}
                  >
                    <option value="">اختر الصف</option>
                    <option value="الأول المتوسط">الأول المتوسط</option>
                    <option value="الثاني المتوسط">الثاني المتوسط</option>
                    <option value="الثالث المتوسط">الثالث المتوسط</option>
                    <option value="الرابع الإعدادي">الرابع الإعدادي</option>
                    <option value="الخامس الإعدادي">الخامس الإعدادي</option>
                    <option value="السادس الإعدادي">السادس الإعدادي</option>
                  </select>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-bold">الشعبة</span>
                  </label>
                  <select
                    className="select select-bordered w-full"
                    value={newStudent.section_name}
                    onChange={(e) => setNewStudent({ ...newStudent, section_name: e.target.value })}
                  >
                    <option value="">اختر الشعبة</option>
                    <option value="أ">أ</option>
                    <option value="ب">ب</option>
                    <option value="ج">ج</option>
                    <option value="د">د</option>
                    <option value="هـ">هـ</option>
                    <option value="و">و</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-2 mt-6">
                <button
                  type="submit"
                  className="btn btn-primary flex-1"
                  disabled={addingStudent}
                >
                  {addingStudent ? (
                    <span className="loading loading-spinner"></span>
                  ) : (
                    <>
                      <i className="fa-solid fa-check ml-1"></i> إضافة
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn btn-ghost"
                >
                  إلغاء
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* قسم الفلترة */}
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

