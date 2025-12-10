import { useRef, useEffect } from 'react'

const VideoPlayer = ({ src, title }) => {
  const videoRef = useRef(null)

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load()
    }
  }, [src])

  return (
    <div className="video-player">
      <video
        ref={videoRef}
        controls
        className="w-full rounded-lg"
        preload="metadata"
      >
        <source src={src} type="video/mp4" />
        متصفحك لا يدعم تشغيل الفيديو
      </video>
    </div>
  )
}

export default VideoPlayer

