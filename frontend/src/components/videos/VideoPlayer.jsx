import { useRef, useEffect, useState } from 'react'
import Hls from 'hls.js'

/**
 * HLS Video Player Component
 * Supports both HLS streaming (.m3u8) and direct video files (MP4)
 * Backward compatible with existing S3 videos
 */
const VideoPlayer = ({
  src,
  hlsSrc,
  title,
  processingStatus,
  thumbnail,
  onReady,
  onError: onErrorCallback
}) => {
  const videoRef = useRef(null)
  const hlsRef = useRef(null)
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)

  // Determine video source - prioritize direct src for backward compatibility
  const videoSource = src || hlsSrc
  const useHls = hlsSrc && hlsSrc.endsWith('.m3u8') && !src

  useEffect(() => {
    const video = videoRef.current
    if (!video || !videoSource) return

    setError(false)
    setLoading(true)

    // Cleanup previous HLS instance
    if (hlsRef.current) {
      hlsRef.current.destroy()
      hlsRef.current = null
    }

    if (useHls && Hls.isSupported()) {
      // Use HLS.js for .m3u8 streams
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: false,
      })

      hlsRef.current = hls

      hls.loadSource(videoSource)
      hls.attachMedia(video)

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        setLoading(false)
        onReady?.()
      })

      hls.on(Hls.Events.ERROR, (event, data) => {
        if (data.fatal) {
          console.error('HLS error:', data)
          setError(true)
          setLoading(false)
          onErrorCallback?.(data)
        }
      })
    } else if (video.canPlayType('application/vnd.apple.mpegurl') && useHls) {
      // Native HLS support (Safari)
      video.src = videoSource
    } else {
      // Direct video file (MP4, etc.) - for S3 videos
      video.src = videoSource
    }

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy()
        hlsRef.current = null
      }
    }
  }, [videoSource, useHls])

  const handleError = () => {
    setError(true)
    setLoading(false)
    console.error('Video playback error:', videoSource)
    onErrorCallback?.({ type: 'PLAYBACK_ERROR', src: videoSource })
  }

  const handleLoadedData = () => {
    setLoading(false)
    setError(false)
  }

  const handleRetry = () => {
    setError(false)
    setLoading(true)
    if (hlsRef.current) {
      hlsRef.current.startLoad()
    } else {
      videoRef.current?.load()
    }
  }

  // Show error state
  if (error) {
    return (
      <div className="bg-gray-100 rounded-lg p-8 text-center aspect-video flex flex-col items-center justify-center">
        <i className="fa-solid fa-video-slash text-4xl text-gray-400 mb-3"></i>
        <p className="text-gray-500">تعذر تشغيل الفيديو</p>
        <p className="text-sm text-gray-400 mt-2">يرجى التحقق من الاتصال أو المحاولة لاحقاً</p>
        <button
          onClick={handleRetry}
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
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg z-10">
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
        poster={thumbnail}
      >
        متصفحك لا يدعم تشغيل الفيديو
      </video>
    </div>
  )
}

export default VideoPlayer
