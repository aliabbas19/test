import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import ProfileImage from '../components/common/ProfileImage'

const Profile = () => {
  const { username } = useParams()
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '',
    address: '',
    phone_number: '',
    father_education: '',
    mother_education: '',
    class_name: '',
    section_name: ''
  })

  useEffect(() => {
    fetchProfile()
  }, [username])

  const fetchProfile = async () => {
    try {
      const response = await api.get(`/api/users/${username}`)
      setUser(response.data)
      setFormData({
        full_name: response.data.full_name || '',
        address: response.data.address || '',
        phone_number: response.data.phone_number || '',
        father_education: response.data.father_education || '',
        mother_education: response.data.mother_education || '',
        class_name: response.data.class_name || '',
        section_name: response.data.section_name || ''
      })
    } catch (error) {
      console.error('Failed to fetch profile:', error)
    } finally {
      setLoading(false)
    }
  }

  // Handle file selection
  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setFormData({ ...formData, profile_image: file })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = new FormData()
      Object.keys(formData).forEach(key => {
        data.append(key, formData[key])
      })

      await api.put('/api/users/me', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setIsEditing(false)
      fetchProfile()
    } catch (error) {
      console.error('Failed to update profile:', error)
      alert('فشل تحديث الملف الشخصي')
    }
  }

  const isOwnProfile = currentUser?.username === username

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    )
  }

  if (!user) {
    return <div>المستخدم غير موجود</div>
  }

  return (
    <div>
      <div>
        {/* Cover Image */}
        <div className="relative h-48 md:h-64 -mx-6 -mt-6 mb-6 overflow-hidden rounded-t-2xl">
          <img
            src="https://i.ibb.co/RkWC7YZm/photo-2025-10-22-12-53-24.jpg"
            alt="غلاف"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-base-100/80 to-transparent"></div>
        </div>

        <div className="glass-effect p-8 rounded-2xl max-w-4xl mx-auto animate-fade-in relative overflow-hidden">
          {/* Decorative background element */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl pointer-events-none"></div>

          <div className="relative z-10">
            <div className="flex flex-col md:flex-row items-center md:items-start justify-between mb-8 gap-6">
              <div className="flex flex-col md:flex-row items-center gap-6 text-center md:text-right">
                <div className="relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-primary to-purple-600 rounded-full opacity-70 blur group-hover:opacity-100 transition duration-500"></div>
                  <div className="relative">
                    <ProfileImage src={isEditing && formData.profile_image instanceof File ? URL.createObjectURL(formData.profile_image) : user.profile_image} size="xl" />
                    {isEditing && (
                      <label className="absolute bottom-0 right-0 btn btn-circle btn-sm btn-primary shadow-lg cursor-pointer">
                        <i className="fa-solid fa-camera"></i>
                        <input type="file" className="hidden" accept="image/*" onChange={handleImageChange} />
                      </label>
                    )}
                  </div>
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-gray-800 mb-2">{user.full_name || user.username}</h2>
                  <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                    <span className="badge badge-primary badge-outline gap-1 p-3">
                      <i className="fa-solid fa-graduation-cap"></i> {user.class_name || 'غير محدد'}
                    </span>
                    <span className="badge badge-secondary badge-outline gap-1 p-3">
                      <i className="fa-solid fa-layer-group"></i> {user.section_name || 'غير محدد'}
                    </span>
                  </div>
                </div>
              </div>
              {isOwnProfile && (
                <button
                  className={`btn ${isEditing ? 'btn-ghost' : 'btn-primary'} shadow-lg gap-2`}
                  onClick={() => setIsEditing(!isEditing)}
                >
                  <i className={`fa-solid ${isEditing ? 'fa-xmark' : 'fa-pen-to-square'}`}></i>
                  {isEditing ? 'إلغاء التعديل' : 'تعديل الملف'}
                </button>
              )}
            </div>

            {user.profile_reset_required && user.role === 'student' && (
              <div className="alert alert-info mb-6 shadow-lg border-2 border-info/20">
                <i className="fa-solid fa-circle-info text-2xl"></i>
                <div className="text-right">
                  <h3 className="font-bold">سنة دراسية جديدة!</h3>
                  <div className="text-xs">الرجاء تحديث الصف والشعبة للمتابعة في استخدام المنصة.</div>
                </div>
              </div>
            )}

            {!user.is_profile_complete && user.role === 'student' && (
              <div className="alert alert-warning mb-6 shadow-lg border-2 border-warning/20">
                <i className="fa-solid fa-triangle-exclamation text-2xl"></i>
                <div>
                  <h3 className="font-bold">حساب غير مكتمل</h3>
                  <div className="text-xs">يجب عليك إكمال جميع الحقول التي تحمل علامة (*) للمتابعة.</div>
                </div>
              </div>
            )}

            {isEditing && isOwnProfile ? (
              <form onSubmit={handleSubmit} className="space-y-6 animate-fade-in-up">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-bold text-gray-600">الاسم الكامل <span className="text-error">*</span></span>
                    </label>
                    <input
                      type="text"
                      className="input input-bordered bg-white/50 focus:bg-white transition-colors"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-bold text-gray-600">رقم الهاتف <span className="text-error">*</span></span>
                    </label>
                    <input
                      type="text"
                      className="input input-bordered bg-white/50 focus:bg-white transition-colors"
                      value={formData.phone_number}
                      onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-control md:col-span-2">
                    <label className="label">
                      <span className="label-text font-bold text-gray-600">العنوان <span className="text-error">*</span></span>
                    </label>
                    <input
                      type="text"
                      className="input input-bordered bg-white/50 focus:bg-white transition-colors"
                      value={formData.address}
                      onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-bold text-gray-600">تحصيل الأب <span className="text-error">*</span></span>
                    </label>
                    <input
                      type="text"
                      className="input input-bordered bg-white/50 focus:bg-white transition-colors"
                      value={formData.father_education}
                      onChange={(e) => setFormData({ ...formData, father_education: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-bold text-gray-600">تحصيل الأم <span className="text-error">*</span></span>
                    </label>
                    <input
                      type="text"
                      className="input input-bordered bg-white/50 focus:bg-white transition-colors"
                      value={formData.mother_education}
                      onChange={(e) => setFormData({ ...formData, mother_education: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-bold text-gray-600">الصف <span className="text-error">*</span></span>
                    </label>
                    <select
                      className="select select-bordered bg-white/50 focus:bg-white transition-colors"
                      value={formData.class_name}
                      onChange={(e) => setFormData({ ...formData, class_name: e.target.value })}
                      required
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
                      <span className="label-text font-bold text-gray-600">الشعبة <span className="text-error">*</span></span>
                    </label>
                    <select
                      className="select select-bordered bg-white/50 focus:bg-white transition-colors"
                      value={formData.section_name}
                      onChange={(e) => setFormData({ ...formData, section_name: e.target.value })}
                      required
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
                <div className="flex gap-4 mt-8 pt-4 border-t border-gray-200/50">
                  <button type="submit" className="btn btn-primary px-8 shadow-lg text-white font-bold">
                    <i className="fa-solid fa-save ml-2"></i> حفظ التغييرات
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={() => setIsEditing(false)}
                  >
                    إلغاء
                  </button>
                </div>
              </form>
            ) : (
              <div className="bg-white/40 rounded-xl p-6 border border-white/50">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-12">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary mt-1">
                      <i className="fa-solid fa-phone"></i>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">رقم الهاتف</p>
                      <p className="font-semibold text-lg">{user.phone_number || 'غير محدد'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary mt-1">
                      <i className="fa-solid fa-location-dot"></i>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">العنوان</p>
                      <p className="font-semibold text-lg">{user.address || 'غير محدد'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary mt-1">
                      <i className="fa-solid fa-user-tie"></i>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">تحصيل الأب</p>
                      <p className="font-semibold text-lg">{user.father_education || 'غير محدد'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary mt-1">
                      <i className="fa-solid fa-user-nurse"></i>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">تحصيل الأم</p>
                      <p className="font-semibold text-lg">{user.mother_education || 'غير محدد'}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
