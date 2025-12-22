import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

const CompleteProfile = () => {
    const { user, refreshUser } = useAuth()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    // Initialize state ONLY ONCE. No background updates will touch this.
    const [formData, setFormData] = useState(() => ({
        full_name: user?.full_name || user?.username || '',
        class_name: user?.class_name || '',
        section_name: user?.section_name || ''
    }))
    const [error, setError] = useState('')

    // Removed useEffect to preventing ANY background resets



    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')

        if (!formData.class_name || !formData.section_name) {
            setError('يرجى اختيار الصف والشعبة')
            return
        }

        setLoading(true)
        try {
            const submitData = new FormData()
            submitData.append('full_name', formData.full_name)
            submitData.append('class_name', formData.class_name)
            submitData.append('section_name', formData.section_name)

            await api.put('/api/users/me', submitData)

            // Update global user state
            if (refreshUser) {
                await refreshUser()
            }

            navigate('/')
        } catch (err) {
            console.error('Profile update failed:', err)
            setError(err.response?.data?.detail || 'فشل تحديث البيانات')
        } finally {
            setLoading(false)
        }
    }

    // If user is already complete, redirect home
    useEffect(() => {
        if (user?.is_profile_complete) {
            navigate('/')
        }
    }, [user, navigate])

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
            <div className="card w-full max-w-md bg-white shadow-xl">
                <div className="card-body">
                    <h2 className="card-title justify-center text-2xl mb-2">إكمال الملف الشخصي</h2>
                    <p className="text-center text-gray-500 mb-6">يرجى إكمال بياناتك للمتابعة</p>

                    {error && (
                        <div className="alert alert-error mb-4 text-sm">
                            <span>{error}</span>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="form-control">
                            <label className="label">
                                <span className="label-text font-bold">الاسم الكامل</span>
                            </label>
                            <input
                                type="text"
                                className="input input-bordered w-full"
                                value={formData.full_name}
                                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                placeholder="اسمك الثلاثي"
                                disabled={loading}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="form-control">
                                <label className="label">
                                    <span className="label-text font-bold">الصف *</span>
                                </label>
                                <select
                                    className="select select-bordered w-full"
                                    value={formData.class_name}
                                    onChange={(e) => setFormData({ ...formData, class_name: e.target.value })}
                                    disabled={loading}
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
                                    <span className="label-text font-bold">الشعبة *</span>
                                </label>
                                <select
                                    className="select select-bordered w-full"
                                    value={formData.section_name}
                                    onChange={(e) => setFormData({ ...formData, section_name: e.target.value })}
                                    disabled={loading}
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

                        <button
                            type="submit"
                            className="btn btn-primary w-full mt-6"
                            disabled={loading}
                        >
                            {loading ? <span className="loading loading-spinner"></span> : 'حفظ ومتابعة'}
                        </button>
                    </form>
                </div>
                <div className="text-center text-xs text-gray-300 pb-2">v4.0 - No Background Sync</div>
            </div>
        </div>
    )
}

export default CompleteProfile
