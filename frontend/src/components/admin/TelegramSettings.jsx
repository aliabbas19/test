import { useState, useEffect } from 'react'
import api from '../../services/api'

const TelegramSettings = () => {
    const [settings, setSettings] = useState({
        bot_token: '',
        chat_id: ''
    })
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [sending, setSending] = useState(false)

    useEffect(() => {
        fetchSettings()
    }, [])

    const fetchSettings = async () => {
        try {
            const response = await api.get('/api/admin/telegram/settings')
            setSettings({
                bot_token: response.data.bot_token || '',
                chat_id: response.data.chat_id || ''
            })
        } catch (error) {
            console.error('Failed to fetch telegram settings:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSave = async (e) => {
        e.preventDefault()
        setSaving(true)
        try {
            await api.put(`/api/admin/telegram/settings?bot_token=${encodeURIComponent(settings.bot_token)}&chat_id=${encodeURIComponent(settings.chat_id)}`)
            alert('تم حفظ إعدادات تيليجرام بنجاح!')
        } catch (error) {
            alert(error.response?.data?.detail || 'حدث خطأ أثناء حفظ الإعدادات')
        } finally {
            setSaving(false)
        }
    }

    const handleSendChampions = async () => {
        if (!settings.bot_token || !settings.chat_id) {
            alert('يرجى إدخال Bot Token و Chat ID أولاً')
            return
        }
        setSending(true)
        try {
            const response = await api.post('/api/admin/telegram/send-champions')
            alert(response.data.message || 'تم الإرسال بنجاح!')
        } catch (error) {
            alert(error.response?.data?.detail || 'حدث خطأ أثناء الإرسال')
        } finally {
            setSending(false)
        }
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center py-12">
                <span className="loading loading-spinner loading-lg text-primary"></span>
            </div>
        )
    }

    return (
        <div className="animate-fade-in max-w-2xl mx-auto">
            <div className="text-center mb-8">
                <i className="fa-brands fa-telegram text-6xl text-blue-500 mb-4"></i>
                <h2 className="text-2xl font-bold mb-2">إعدادات تيليجرام</h2>
                <p className="text-gray-600">إعداد البوت لإرسال تقارير الأبطال</p>
            </div>

            {/* Settings Form */}
            <form onSubmit={handleSave} className="space-y-6 bg-white/50 p-6 rounded-2xl border border-white/30 mb-8">
                <div className="form-control">
                    <label className="label">
                        <span className="label-text font-bold text-gray-700">
                            <i className="fa-solid fa-key ml-2 text-primary"></i>
                            Bot Token
                        </span>
                    </label>
                    <input
                        type="text"
                        className="input input-bordered bg-white/70 focus:bg-white transition-colors font-mono text-sm"
                        placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz..."
                        value={settings.bot_token}
                        onChange={(e) => setSettings({ ...settings, bot_token: e.target.value })}
                        dir="ltr"
                    />
                    <label className="label">
                        <span className="label-text-alt text-gray-500">
                            يمكنك الحصول عليه من @BotFather في تيليجرام
                        </span>
                    </label>
                </div>

                <div className="form-control">
                    <label className="label">
                        <span className="label-text font-bold text-gray-700">
                            <i className="fa-solid fa-hashtag ml-2 text-primary"></i>
                            Chat ID
                        </span>
                    </label>
                    <input
                        type="text"
                        className="input input-bordered bg-white/70 focus:bg-white transition-colors font-mono text-sm"
                        placeholder="-1001234567890"
                        value={settings.chat_id}
                        onChange={(e) => setSettings({ ...settings, chat_id: e.target.value })}
                        dir="ltr"
                    />
                    <label className="label">
                        <span className="label-text-alt text-gray-500">
                            يمكنك الحصول عليه من @userinfobot أو من رابط القناة/المجموعة
                        </span>
                    </label>
                </div>

                <button
                    type="submit"
                    className={`btn btn-primary w-full gap-2 ${saving ? 'loading' : ''}`}
                    disabled={saving}
                >
                    {!saving && <i className="fa-solid fa-save"></i>}
                    {saving ? 'جاري الحفظ...' : 'حفظ الإعدادات'}
                </button>
            </form>

            {/* Send Champions Section */}
            <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 p-6 rounded-2xl border border-blue-500/20 text-center">
                <h3 className="text-xl font-bold mb-3 text-gray-800">
                    <i className="fa-solid fa-trophy text-yellow-500 ml-2"></i>
                    إرسال القائمة الذهبية
                </h3>
                <p className="text-gray-600 mb-4">
                    نشر قائمة الطلاب المتميزين (الأبطال) لهذا الأسبوع إلى قناة التيليجرام.
                </p>
                <button
                    className={`btn btn-lg shadow-xl shadow-blue-500/30 ${settings.bot_token && settings.chat_id ? 'btn-primary' : 'btn-disabled'} ${sending ? 'loading' : ''}`}
                    onClick={handleSendChampions}
                    disabled={sending || !settings.bot_token || !settings.chat_id}
                >
                    {!sending && <i className="fa-solid fa-paper-plane ml-2"></i>}
                    {sending ? 'جاري الإرسال...' : 'إرسال الآن'}
                </button>
                {(!settings.bot_token || !settings.chat_id) && (
                    <p className="text-warning text-sm mt-3">
                        <i className="fa-solid fa-exclamation-triangle ml-1"></i>
                        يرجى حفظ إعدادات البوت أولاً
                    </p>
                )}
            </div>
        </div>
    )
}

export default TelegramSettings
