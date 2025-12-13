import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useAuth } from '../../context/AuthContext'

const GroupMessageSender = ({ onClose }) => {
    const { isAdmin } = useAuth()
    const [classes, setClasses] = useState([])
    const [sections, setSections] = useState([])
    const [selectedClass, setSelectedClass] = useState('')
    const [selectedSection, setSelectedSection] = useState('')
    const [message, setMessage] = useState('')
    const [sending, setSending] = useState(false)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchFilters()
    }, [])

    const fetchFilters = async () => {
        try {
            // Fetch unique classes and sections from users
            const response = await api.get('/api/users', { params: { role: 'student' } })
            const students = response.data

            // Extract unique classes
            const uniqueClasses = [...new Set(students.map(s => s.class_name).filter(Boolean))]
            setClasses(uniqueClasses)

            // Extract unique sections
            const uniqueSections = [...new Set(students.map(s => s.section_name).filter(Boolean))]
            setSections(uniqueSections)
        } catch (error) {
            console.error('Failed to fetch filters:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSend = async (e) => {
        e.preventDefault()

        if (!selectedClass) {
            alert('يرجى اختيار الصف أولاً')
            return
        }

        if (!message.trim()) {
            alert('يرجى كتابة الرسالة')
            return
        }

        setSending(true)
        try {
            await api.post('/api/messages', {
                type: 'group',
                content: message,
                class_name: selectedClass,
                section_name: selectedSection || null
            })

            const targetDesc = selectedSection
                ? `${selectedClass} - ${selectedSection}`
                : `جميع طلاب ${selectedClass}`

            alert(`تم إرسال الرسالة بنجاح إلى ${targetDesc}`)
            setMessage('')
            if (onClose) onClose()
        } catch (error) {
            alert(error.response?.data?.detail || 'حدث خطأ أثناء إرسال الرسالة')
        } finally {
            setSending(false)
        }
    }

    if (!isAdmin) return null

    if (loading) {
        return (
            <div className="flex justify-center items-center py-8">
                <span className="loading loading-spinner loading-md text-primary"></span>
            </div>
        )
    }

    return (
        <div className="bg-gradient-to-br from-purple-500/5 to-blue-500/5 p-6 rounded-2xl border border-purple-500/20">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold flex items-center gap-2 text-gray-800">
                    <i className="fa-solid fa-users text-purple-500"></i>
                    إرسال رسالة جماعية
                </h3>
                {onClose && (
                    <button onClick={onClose} className="btn btn-sm btn-circle btn-ghost">
                        <i className="fa-solid fa-xmark"></i>
                    </button>
                )}
            </div>

            <form onSubmit={handleSend} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text font-bold">
                                <i className="fa-solid fa-graduation-cap text-primary ml-1"></i>
                                الصف <span className="text-error">*</span>
                            </span>
                        </label>
                        <select
                            className="select select-bordered bg-white/70 focus:bg-white"
                            value={selectedClass}
                            onChange={(e) => setSelectedClass(e.target.value)}
                            required
                        >
                            <option value="">اختر الصف</option>
                            {classes.map((cls) => (
                                <option key={cls} value={cls}>{cls}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-control">
                        <label className="label">
                            <span className="label-text font-bold">
                                <i className="fa-solid fa-layer-group text-primary ml-1"></i>
                                الشعبة (اختياري)
                            </span>
                        </label>
                        <select
                            className="select select-bordered bg-white/70 focus:bg-white"
                            value={selectedSection}
                            onChange={(e) => setSelectedSection(e.target.value)}
                        >
                            <option value="">كل الشعب</option>
                            {sections.map((sec) => (
                                <option key={sec} value={sec}>{sec}</option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="form-control">
                    <label className="label">
                        <span className="label-text font-bold">
                            <i className="fa-solid fa-message text-primary ml-1"></i>
                            نص الرسالة
                        </span>
                    </label>
                    <textarea
                        className="textarea textarea-bordered bg-white/70 focus:bg-white min-h-[120px]"
                        placeholder="اكتب الرسالة التي تريد إرسالها لجميع الطلاب..."
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        required
                    ></textarea>
                </div>

                {selectedClass && (
                    <div className="alert alert-info py-2">
                        <i className="fa-solid fa-circle-info"></i>
                        <span>
                            سيتم الإرسال إلى: <strong>
                                {selectedSection ? `${selectedClass} - ${selectedSection}` : `جميع طلاب ${selectedClass}`}
                            </strong>
                        </span>
                    </div>
                )}

                <button
                    type="submit"
                    className={`btn btn-primary w-full gap-2 ${sending ? 'loading' : ''}`}
                    disabled={sending || !selectedClass || !message.trim()}
                >
                    {!sending && <i className="fa-solid fa-paper-plane"></i>}
                    {sending ? 'جاري الإرسال...' : 'إرسال الرسالة الجماعية'}
                </button>
            </form>
        </div>
    )
}

export default GroupMessageSender
