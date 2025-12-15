import { useState, useEffect } from 'react'
import api from '../services/api'
import VideoCard from '../components/videos/VideoCard'
import VideoUpload from '../components/videos/VideoUpload'
import PostCard from '../components/posts/PostCard'
import { useAuth } from '../context/AuthContext'

const Home = () => {
  const { isAdmin } = useAuth()
  const [videos, setVideos] = useState([])
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)

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
          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
              <i className="fa-solid fa-bullhorn text-primary"></i> إنشاء منشور
            </h3>
            <form onSubmit={handleCreatePost}>
              <textarea
                name="content"
                className="textarea textarea-bordered w-full mb-3 bg-gray-50 text-gray-800 border-gray-300"
                placeholder="اكتب إعلانك أو نشاطك هنا..."
                required
              ></textarea>
              <button type="submit" className="btn btn-primary w-full text-white font-bold">
                <i className="fa-solid fa-paper-plane ml-2"></i> نشر
              </button>
            </form>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
              <i className="fa-solid fa-cloud-arrow-up text-primary"></i> رفع فيديو
            </h3>
            <VideoUpload onUpload={fetchVideos} />
          </div>
        </div>
      )}

      {/* Posts Section */}
      {posts.length > 0 && (
        <div className="mb-12">
          <div className="bg-white rounded-xl shadow-md border border-gray-200 p-4 mb-8">
            <h2 className="text-2xl lg:text-3xl font-bold text-center text-gray-800">
              <i className="fa-solid fa-bullhorn text-primary ml-2"></i>
              المنشورات والإعلانات
            </h2>
          </div>
          <div className="max-w-3xl mx-auto">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 mb-8">
        <form className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 items-end">
          <div className="form-control">
            <label className="label"><span className="label-text font-bold text-gray-700">المرحلة</span></label>
            <select name="class_name" className="select select-bordered w-full bg-gray-50 text-gray-800 border-gray-300" onChange={handleFilterChange}>
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
            <label className="label"><span className="label-text font-bold text-gray-700">الشعبة</span></label>
            <select name="section_name" className="select select-bordered w-full bg-gray-50 text-gray-800 border-gray-300" onChange={handleFilterChange}>
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
            <label className="label"><span className="label-text font-bold text-gray-700">النوع</span></label>
            <select name="video_type" className="select select-bordered w-full bg-gray-50 text-gray-800 border-gray-300" onChange={handleFilterChange}>
              <option value="">الكل</option>
              <option value="منهجي">منهجي</option>
              <option value="اثرائي">اثرائي</option>
            </select>
          </div>
        </form>
      </div>

      {/* Videos Section */}
      <div className="mb-8">
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-4 mb-8">
          <h2 className="text-2xl lg:text-3xl font-bold text-center text-gray-800">
            <i className="fa-solid fa-video text-primary ml-2"></i>
            المحاضرات الفيديوية
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {videos.map((video) => (
            <VideoCard key={video.id} video={video} onApprove={fetchVideos} />
          ))}
        </div>
      </div>

      {videos.length === 0 && posts.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl shadow-md border border-gray-200">
          <i className="fa-solid fa-box-open text-6xl text-gray-300 mb-4"></i>
          <p className="text-gray-500 text-lg">لا توجد بيانات للعرض حالياً</p>
        </div>
      )}
    </div>
  )
}

export default Home
