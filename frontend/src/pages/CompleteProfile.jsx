import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

const CompleteProfile = () => {
    const { user, refreshUser } = useAuth()
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState(false)

    const [formData, setFormData] = useState(() => {
        try {
            const saved = localStorage.getItem('profile_autosave')
            if (saved) {
                return JSON.parse(saved)
            }
        } catch (e) {
            console.error('Failed to load saved form', e)
        }

        return {
            full_name: user?.full_name || user?.username || '',
            class_name: user?.class_name || '',
            section_name: user?.section_name || ''
        }
    })

    useEffect(() => {
        const saved = localStorage.getItem('profile_autosave')
        if (!saved && user) {
            setFormData(prev => ({
                full_name: prev.full_name || user.full_name || user.username || '',
                class_name: prev.class_name || user.class_name || '',
                section_name: prev.section_name || user.section_name || ''
            }))
        }
    }, [user])

    useEffect(() => {
        localStorage.setItem('profile_autosave', JSON.stringify(formData))
    }, [formData])

    useEffect(() => {
        if (user?.is_profile_complete) {
            window.location.href = '/'
        }
    }, [user])

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setSuccess(false)

        if (!formData.class_name || !formData.section_name) {
            setError('يرجى اختيار الصف والشعبة')
            return
        }

        setLoading(true)
        try {
            const submitData = new FormData()
            submitData.append('full_name', formData.full_name || user?.username || 'Student')
            submitData.append('class_name', formData.class_name)
            submitData.append('section_name', formData.section_name)

            await api.put('/api/users/me', submitData)

            localStorage.removeItem('profile_autosave')
            setSuccess(true)

            if (refreshUser) {
                await refreshUser()
            }

            setTimeout(() => {
                window.location.href = '/'
            }, 500)

        } catch (err) {
            console.error('Profile update failed:', err)
            setError(err.response?.data?.detail || 'فشل تحديث البيانات')
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4" dir="rtl">
            <div className="card w-full max-w-md bg-white shadow-xl">
                <div className="card-body">
                    <h2 className="card-title justify-center text-2xl mb-2">إكمال الملف الشخصي</h2>
                    <p className="text-center text-gray-500 mb-6">يرجى إكمال بياناتك للمتابعة</p>

                    {error && (
                        <div className="alert alert-error mb-4 text-sm">
                            <span>{error}</span>
                        </div>
                    )}

                    {success && (
                        <div className="alert alert-success mb-4 text-sm">
                            <span>تم الحفظ بنجاح! جاري التحويل...</span>
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
                            disabled={loading || success}
                        >
                            {loading ? <span className="loading loading-spinner"></span> : (success ? 'تم الحفظ ✓' : 'حفظ ومتابعة')}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default CompleteProfile
