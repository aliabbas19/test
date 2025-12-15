import { useRef, useEffect, useState } from 'react'

const VideoPlayer = ({ src, title }) => {
  const videoRef = useRef(null)
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (videoRef.current) {
      setError(false)
      setLoading(true)
      videoRef.current.load()
    }
  }, [src])

  const handleError = () => {
    setError(true)
    setLoading(false)
    console.error('Video playback error:', src)
  }

  const handleLoadedData = () => {
    setLoading(false)
    setError(false)
  }

  if (error) {
    return (
      <div className="bg-gray-100 rounded-lg p-8 text-center">
        <i className="fa-solid fa-video-slash text-4xl text-gray-400 mb-3"></i>
        <p className="text-gray-500">تعذر تشغيل الفيديو</p>
        <p className="text-sm text-gray-400 mt-2">يرجى التحقق من الاتصال أو المحاولة لاحقاً</p>
        <button
          onClick={() => {
            setError(false)
            setLoading(true)
            videoRef.current?.load()
          }}
          className="btn btn-sm btn-primary mt-3"
        >
          <i className="fa-solid fa-rotate-right ml-1"></i> إعادة المحاولة
        </button>
      </div>
    )
  }

  return (
    <div className="video-player relative">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg">
          <span className="loading loading-spinner loading-lg text-primary"></span>
        </div>
      )}
      <video
        ref={videoRef}
        controls
        className="w-full rounded-lg"
        preload="metadata"
        onError={handleError}
        onLoadedData={handleLoadedData}
        playsInline
      >
        <source src={src} type="video/mp4" />
        <source src={src} type="video/webm" />
        <source src={src} type="video/ogg" />
        متصفحك لا يدعم تشغيل الفيديو
      </video>
    </div>
  )
}

export default VideoPlayer


