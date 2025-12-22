import { useState, useEffect } from 'react'
import api from '../services/api'
import VideoCard from '../components/videos/VideoCard'
import VideoUpload from '../components/videos/VideoUpload'
import PostCard from '../components/posts/PostCard'
import { useAuth } from '../context/AuthContext'

import ImageSlider from '../components/common/ImageSlider'

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
    <div className="space-y-6 animate-fade-in">
      {/* Image Slider */}
      <ImageSlider />

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

      {/* Student: Upload Video (with pending approval notice) */}
      {!isAdmin && (
        <div className="mb-8">
          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 max-w-2xl mx-auto">
            <h3 className="text-xl font-bold mb-2 flex items-center gap-2 text-gray-800">
              <i className="fa-solid fa-cloud-arrow-up text-primary"></i> رفع فيديو
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              <i className="fa-solid fa-info-circle ml-1"></i>
              ملاحظة: سيتم مراجعة الفيديو من قبل المشرف قبل نشره
            </p>
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
        <h3 className="font-bold text-gray-700 mb-4 flex items-center gap-2">
          <i className="fa-solid fa-filter text-primary"></i> تصفية المحتوى
        </h3>

        <div className="space-y-6">
          {/* Class Filter */}
          <div>
            <label className="text-sm font-bold text-gray-500 mb-2 block">المرحلة الدراسية</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setFilters({ ...filters, class_name: '' })}
                className={`btn btn-sm ${!filters.class_name ? 'btn-primary text-white' : 'btn-ghost bg-gray-100'}`}
              >
                الكل
              </button>
              {['الأول المتوسط', 'الثاني المتوسط', 'الثالث المتوسط', 'الرابع الإعدادي', 'الخامس الإعدادي', 'السادس الإعدادي'].map(cls => (
                <button
                  key={cls}
                  onClick={() => setFilters({ ...filters, class_name: cls })}
                  className={`btn btn-sm ${filters.class_name === cls ? 'btn-primary text-white' : 'btn-ghost bg-gray-100 text-gray-600'}`}
                >
                  {cls}
                </button>
              ))}
            </div>
          </div>

          {/* Section Filter */}
          <div>
            <label className="text-sm font-bold text-gray-500 mb-2 block">الشعبة</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setFilters({ ...filters, section_name: '' })}
                className={`btn btn-sm ${!filters.section_name ? 'btn-primary text-white' : 'btn-ghost bg-gray-100'}`}
              >
                الكل
              </button>
              {['أ', 'ب', 'ج', 'د', 'هـ', 'و'].map(sec => (
                <button
                  key={sec}
                  onClick={() => setFilters({ ...filters, section_name: sec })}
                  className={`btn btn-sm ${filters.section_name === sec ? 'btn-primary text-white' : 'btn-ghost bg-gray-100 text-gray-600'}`}
                >
                  {sec}
                </button>
              ))}
            </div>
          </div>

          {/* Type Filter - The "Ratings" replacement */}
          <div>
            <label className="text-sm font-bold text-gray-500 mb-2 block">نوع المحتوى</label>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setFilters({ ...filters, video_type: '' })}
                className={`btn ${!filters.video_type ? 'btn-primary text-white' : 'btn-outline border-gray-300 text-gray-600 hover:bg-gray-50 hover:border-gray-400'}`}
              >
                الكل
              </button>
              <button
                onClick={() => setFilters({ ...filters, video_type: 'منهجي' })}
                className={`btn gap-2 ${filters.video_type === 'منهجي' ? 'btn-info text-white' : 'btn-outline border-gray-300 text-gray-600 hover:bg-info hover:text-white hover:border-info'}`}
              >
                <i className="fa-solid fa-book"></i> منهجي
              </button>
              <button
                onClick={() => setFilters({ ...filters, video_type: 'اثرائي' })}
                className={`btn gap-2 ${filters.video_type === 'اثرائي' ? 'btn-warning text-white' : 'btn-outline border-gray-300 text-gray-600 hover:bg-warning hover:text-white hover:border-warning'}`}
              >
                <i className="fa-solid fa-star"></i> اثرائي
              </button>
            </div>
          </div>
        </div>
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
            <VideoCard
              key={video.id}
              video={video}
              onApprove={fetchVideos}
              onDelete={(videoId) => setVideos(videos.filter(v => v.id !== videoId))}
            />
          ))}
        </div>
      </div>

      {
        videos.length === 0 && posts.length === 0 && (
          <div className="text-center py-12 bg-white rounded-xl shadow-md border border-gray-200">
            <i className="fa-solid fa-box-open text-6xl text-gray-300 mb-4"></i>
            <p className="text-gray-500 text-lg">لا توجد بيانات للعرض حالياً</p>
          </div>
        )
      }
    </div >
  )
}

export default Home
