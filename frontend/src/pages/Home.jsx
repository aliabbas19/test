import { useState, useEffect } from 'react'
import api from '../services/api'
import VideoCard from '../components/videos/VideoCard'
import VideoUpload from '../components/videos/VideoUpload'
import CommentSection from '../components/comments/CommentSection'
import VideoReview from '../components/videos/VideoReview'
import PostCard from '../components/posts/PostCard'
import { useAuth } from '../context/AuthContext'

const Home = () => {
  const { isAdmin } = useAuth()
  const [videos, setVideos] = useState([])
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedVideo, setSelectedVideo] = useState(null)

  // Filters
  const [filters, setFilters] = useState({
    class_name: '',
    section_name: '',
    video_type: '',
    start_date: '',
    end_date: ''
  })

  useEffect(() => {
    fetchVideos()
    fetchPosts()
  }, [])

  useEffect(() => {
    fetchVideos()
  }, [filters])

  const fetchVideos = async () => {
    try {
      const params = { is_archived: false, ...filters }
      const response = await api.get('/api/videos', { params })
      setVideos(response.data)
    } catch (error) {
      console.error('Failed to fetch videos:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPosts = async () => {
    try {
      const response = await api.get('/api/posts')
      setPosts(response.data)
    } catch (error) {
      console.error('Failed to fetch posts:', error)
    }
  }

  const handleCreatePost = async (e) => {
    e.preventDefault()
    const content = e.target.content.value
    if (!content) return

    try {
      await api.post('/api/posts', { content })
      e.target.reset()
      fetchPosts()
    } catch (error) {
      console.error("Failed to create post", error)
    }
  }

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value })
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
      {/* Admin: Create Post / Upload Video */}
      {isAdmin && (
        <div className="mb-8 grid gap-6 md:grid-cols-2">
          <div className="glass-effect p-6 rounded-xl">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <i className="fa-solid fa-bullhorn text-primary"></i> إنشاء منشور
            </h3>
            <form onSubmit={handleCreatePost}>
              <textarea
                name="content"
                className="textarea textarea-bordered w-full mb-3 bg-white/50"
                placeholder="اكتب إعلانك أو نشاطك هنا..."
                required
              ></textarea>
              <button type="submit" className="btn btn-primary w-full text-white font-bold shadow-lg">
                <i className="fa-solid fa-paper-plane ml-2"></i> نشر
              </button>
            </form>
          </div>

          <div className="glass-effect p-6 rounded-xl">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <i className="fa-solid fa-cloud-arrow-up text-primary"></i> رفع فيديو
            </h3>
            <VideoUpload onUpload={fetchVideos} />
          </div>
        </div>
      )}

      {/* Posts Section */}
      {posts.length > 0 && (
        <div className="mb-12">
          <div className="ship-frame text-2xl lg:text-3xl mb-8">
            <span className="animate-text-gradient bg-gradient-to-r from-primary via-purple-600 to-primary bg-[length:200%_auto] bg-clip-text text-transparent">
              المنشورات والإعلانات
            </span>
          </div>
          <div className="max-w-3xl mx-auto">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="glass-effect p-6 rounded-xl mb-8">
        <form className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
          <div className="form-control">
            <label className="label"><span className="label-text font-bold">المرحلة</span></label>
            <select name="class_name" className="select select-bordered w-full bg-white/50" onChange={handleFilterChange}>
              <option value="">الكل</option>
              <option value="الأول المتوسط">الأول المتوسط</option>
              <option value="الثاني المتوسط">الثاني المتوسط</option>
              <option value="الثالث المتوسط">الثالث المتوسط</option>
              <option value="الرابع الإعدادي">الرابع الإعدادي</option>
              <option value="الخامس الإعدادي">الخامس الإعدادي</option>
              <option value="السادس الإعدادي">السادس الإعدادي</option>
            </select>
          </div>
          <div className="form-control">
            <label className="label"><span className="label-text font-bold">الشعبة</span></label>
            <select name="section_name" className="select select-bordered w-full bg-white/50" onChange={handleFilterChange}>
              <option value="">الكل</option>
              <option value="أ">أ</option>
              <option value="ب">ب</option>
              <option value="ج">ج</option>
              <option value="د">د</option>
              <option value="هـ">هـ</option>
              <option value="و">و</option>
            </select>
          </div>
          <div className="form-control">
            <label className="label"><span className="label-text font-bold">النوع</span></label>
            <select name="video_type" className="select select-bordered w-full bg-white/50" onChange={handleFilterChange}>
              <option value="">الكل</option>
              <option value="منهجي">منهجي</option>
              <option value="اثرائي">اثرائي</option>
            </select>
          </div>
          {/* Note: Date filtering needs backend support or client-side filtering. Passing to backend for now. */}
        </form>
      </div>

      {/* Videos Section */}
      <div className="mb-8">
        <div className="ship-frame text-2xl lg:text-3xl mb-8">
          <span className="animate-text-gradient bg-gradient-to-r from-green-500 via-primary to-green-500 bg-[length:200%_auto] bg-clip-text text-transparent">
            المحاضرات الفديوية
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {videos.map((video) => (
            <div key={video.id}>
              <VideoCard video={video} onSelect={() => setSelectedVideo(video)} />
              {selectedVideo?.id === video.id && (
                <div className="glass-effect p-4 rounded-xl mt-4 border border-primary/20 animate-superhero-glow">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-lg text-primary">تفاصيل الفيديو</h3>
                    <button onClick={() => setSelectedVideo(null)} className="btn btn-sm btn-circle btn-ghost">
                      <i className="fa-solid fa-xmark"></i>
                    </button>
                  </div>
                  {isAdmin && <VideoReview video={video} onUpdate={fetchVideos} />}
                  <CommentSection videoId={video.id} />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {videos.length === 0 && posts.length === 0 && (
        <div className="text-center py-12 glass-effect rounded-xl">
          <i className="fa-solid fa-box-open text-6xl text-gray-300 mb-4"></i>
          <p className="text-gray-500 text-lg">لا توجد بيانات للعرض حالياً</p>
        </div>
      )}
    </div>
  )
}

export default Home
