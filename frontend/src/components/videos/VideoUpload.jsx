import { useState } from 'react'
import api from '../../services/api'
import axios from 'axios'

const VideoUpload = ({ onUpload }) => {
  const [title, setTitle] = useState('')
  const [videoType, setVideoType] = useState('منهجي')
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file || !title) return

    if (!navigator.onLine) {
      alert('لا يتوفر اتصال بالإنترنت. يرجى التحقق من اتصالك والمحاولة مرة أخرى.')
      return
    }

    setUploading(true)
    const formData = new FormData()
    formData.append('title', title)
    formData.append('video_type', videoType)
    formData.append('video_file', file)

    try {
      // 1. Get Presigned URL
      const presignedResponse = await api.post('/api/uploads/presigned-url', {
        filename: file.name,
        file_type: 'video',
        content_type: file.type,
        title: title,
        video_type: videoType
      })

      const { upload_url, video_id, key } = presignedResponse.data

      // 2. Upload to S3 directly
      // Use clean axios instance to avoid auth headers
      await axios.put(upload_url, file, {
        headers: {
          'Content-Type': presignedResponse.data.content_type || file.type
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          setProgress(percentCompleted)
        }
      })

      // 3. Notify Backend
      await api.post('/api/uploads/upload-complete', {
        video_id: video_id,
        s3_key: key
      })

      alert('Video uploaded successfully! Processing started.')
      setTitle('')
      setFile(null)
      setProgress(0)
      if (onUpload) onUpload()
    } catch (error) {
      console.error('Upload failed:', error)
      alert(error.response?.data?.detail || 'فشل رفع الفيديو')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">رفع فيديو جديد</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-control mb-4">
            <label className="label">
              <span className="label-text">عنوان الفيديو</span>
            </label>
            <input
              type="text"
              className="input input-bordered"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-control mb-4">
            <label className="label">
              <span className="label-text">نوع الفيديو</span>
            </label>
            <select
              className="select select-bordered"
              value={videoType}
              onChange={(e) => setVideoType(e.target.value)}
            >
              <option value="منهجي">منهجي (60 ثانية)</option>
              <option value="اثرائي">اثرائي (240 ثانية)</option>
            </select>
          </div>

          <div className="form-control mb-4">
            <label className="label">
              <span className="label-text">ملف الفيديو</span>
            </label>
            <input
              type="file"
              className="file-input file-input-bordered"
              accept="video/*"
              onChange={(e) => setFile(e.target.files[0])}
              required
            />
          </div>

          {uploading && (
            <progress
              className="progress progress-primary w-full mb-4"
              value={progress}
              max="100"
            ></progress>
          )}

          <button
            type="submit"
            className="btn btn-primary w-full"
            disabled={uploading}
          >
            {uploading ? 'جاري الرفع...' : 'رفع الفيديو'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default VideoUpload

