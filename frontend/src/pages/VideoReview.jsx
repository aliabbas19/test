import { useState, useEffect } from 'react'
import api from '../services/api'
import VideoCard from '../components/videos/VideoCard'

const VideoReview = () => {
    const [videos, setVideos] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchPendingVideos()
    }, [])

    const fetchPendingVideos = async () => {
        try {
            // Fetch only unapproved videos
            const response = await api.get('/api/videos', {
                params: { is_approved: false }
            })
            setVideos(response.data)
        } catch (error) {
            console.error('Failed to fetch pending videos:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleApprove = async (videoId) => {
        if (!confirm('هل أنت متأكد من الموافقة على هذا الفيديو؟')) return

        try {
            await api.post(`/api/videos/${videoId}/approve`)
            // Remove from list
            setVideos(videos.filter(v => v.id !== videoId))
            alert('تمت الموافقة على الفيديو بنجاح')
        } catch (error) {
            console.error('Failed to approve video:', error)
            alert('حدث خطأ أثناء الموافقة')
        }
    }

    const handleDelete = async (videoId) => {
        if (!confirm('هل أنت متأكد من حذف هذا الفيديو؟ لا يمكن التراجع عن هذا الإجراء.')) return

        try {
            await api.delete(`/api/videos/${videoId}`)
            setVideos(videos.filter(v => v.id !== videoId))
            alert('تم حذف الفيديو بنجاح')
        } catch (error) {
            console.error('Failed to delete video:', error)
            alert('حدث خطأ أثناء الحذف')
        }
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-[50vh]">
                <span className="loading loading-spinner loading-lg text-primary"></span>
            </div>
        )
    }

    return (
        <div>
            <div className="ship-frame text-2xl lg:text-3xl mb-8 mx-auto w-fit">
                <span className="animate-text-gradient bg-gradient-to-r from-orange-600 via-primary to-orange-600 bg-[length:200%_auto] bg-clip-text text-transparent">
                    مراجعة الفيديوهات المعلقة
                </span>
            </div>

            {videos.length === 0 ? (
                <div className="glass-effect p-12 rounded-xl text-center flex flex-col items-center">
                    <div className="w-24 h-24 rounded-full bg-green-500/10 flex items-center justify-center mb-4">
                        <i className="fa-solid fa-check-double text-4xl text-green-500"></i>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-700 mb-2">ممتاز!</h2>
                    <p className="text-gray-500 text-lg">لا توجد فيديوهات بانتظار المراجعة حالياً.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {videos.map((video) => (
                        <div key={video.id} className="relative group">
                            <VideoCard video={video} showActions={false} />

                            {/* Admin Actions Overlay */}
                            <div className="absolute inset-x-0 bottom-0 p-3 bg-white/90 backdrop-blur-md border-t border-white/20 rounded-b-2xl flex gap-2 translate-y-full opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 z-10">
                                <button
                                    onClick={() => handleApprove(video.id)}
                                    className="btn btn-success flex-1 text-white gap-2 shadow-lg hover:brightness-110"
                                >
                                    <i className="fa-solid fa-check"></i> موافقة
                                </button>
                                <button
                                    onClick={() => handleDelete(video.id)}
                                    className="btn btn-error flex-1 text-white gap-2 shadow-lg hover:brightness-110"
                                >
                                    <i className="fa-solid fa-trash"></i> حذف
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default VideoReview
