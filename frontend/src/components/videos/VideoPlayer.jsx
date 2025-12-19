import { useRef, useEffect, useState } from 'react'
import Hls from 'hls.js'

/**
 * HLS Video Player Component
 * Supports both HLS streaming (.m3u8) and fallback to direct video files
 * Optimized for zero-buffering experience
 */
const VideoPlayer = ({
  src,
  hlsSrc,  // HLS playlist URL (optional, preferred)
  title,
  processingStatus = 'ready',  // pending, processing, ready, failed
  thumbnail,
  onReady,
  onError: onErrorCallback
}) => {
  const videoRef = useRef(null)
  const hlsRef = useRef(null)
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)
  const [isProcessing, setIsProcessing] = useState(processingStatus !== 'ready')

  // Determine if we should use HLS
  const useHls = hlsSrc && (hlsSrc.endsWith('.m3u8') || hlsSrc.includes('/hls/'))
  const videoSource = useHls ? hlsSrc : src

  useEffect(() => {
    setIsProcessing(processingStatus !== 'ready')
  }, [processingStatus])

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
      // Use HLS.js for browsers that don't natively support HLS
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: false,
        backBufferLength: 90,
        maxBufferLength: 30,
        maxMaxBufferLength: 60,
        // Preload first segments for instant playback
        startLevel: -1,
        autoStartLoad: true,
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
          console.error('HLS fatal error:', data)
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              // Try to recover from network error
              hls.startLoad()
              break
            case Hls.ErrorTypes.MEDIA_ERROR:
              hls.recoverMediaError()
              break
            default:
              setError(true)
              setLoading(false)
              onErrorCallback?.(data)
              break
          }
        }
      })
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS support (Safari, iOS)
      video.src = videoSource
      video.addEventListener('loadeddata', () => {
        setLoading(false)
        onReady?.()
      })
    } else if (src) {
      // Fallback to direct video source (MP4)
      video.src = src
      video.addEventListener('loadeddata', () => {
        setLoading(false)
        onReady?.()
      })
    }

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy()
        hlsRef.current = null
      }
    }
  }, [videoSource, src, useHls])

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

  // Show processing state
  if (isProcessing) {
    return (
      <div className="bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg p-8 text-center aspect-video flex flex-col items-center justify-center">
        {thumbnail ? (
          <img
            src={thumbnail}
            alt={title}
            className="absolute inset-0 w-full h-full object-cover opacity-50 rounded-lg"
          />
        ) : null}
        <div className="relative z-10">
          <span className="loading loading-spinner loading-lg text-primary mb-3"></span>
          <p className="text-gray-600 font-medium">جاري معالجة الفيديو...</p>
          <p className="text-sm text-gray-400 mt-1">
            {processingStatus === 'pending' && 'في انتظار المعالجة'}
            {processingStatus === 'processing' && 'يتم تحويل الفيديو للبث السريع'}
            {processingStatus === 'failed' && 'فشلت المعالجة'}
          </p>
        </div>
      </div>
    )
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
      {thumbnail && loading && (
        <img
          src={thumbnail}
          alt={title}
          className="absolute inset-0 w-full h-full object-cover rounded-lg"
        />
      )}
      <video
        ref={videoRef}
        controls
        className="w-full rounded-lg"
        preload="auto"
        onError={handleError}
        onLoadedData={handleLoadedData}
        playsInline
        poster={thumbnail}
      >
        {/* Fallback sources for browsers without HLS support */}
        {!useHls && src && <source src={src} type="video/mp4" />}
        متصفحك لا يدعم تشغيل الفيديو
      </video>
    </div>
  )
}

export default VideoPlayer
