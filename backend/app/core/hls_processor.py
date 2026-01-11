"""
HLS Video Processor Service
Converts uploaded videos to HLS format using FFmpeg for smooth streaming.
"""
import os
import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# HLS Configuration
HLS_SEGMENT_DURATION = 4  # seconds per segment
HLS_PLAYLIST_TYPE = "vod"  # Video on Demand
HLS_OUTPUT_DIR = "/app/hls"  # Docker container path


class HLSProcessor:
    """Handles video transcoding to HLS format"""
    
    def __init__(self, output_base_dir: str = HLS_OUTPUT_DIR):
        self.output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)
    
    def get_video_output_dir(self, video_id: int) -> str:
        """Get the output directory for a specific video"""
        return os.path.join(self.output_base_dir, str(video_id))
    
    def get_playlist_path(self, video_id: int) -> str:
        """Get the path to the HLS playlist file"""
        return os.path.join(self.get_video_output_dir(video_id), "playlist.m3u8")
    
    def get_playlist_url(self, video_id: int) -> str:
        """Get the URL path for the HLS playlist"""
        return f"/hls/{video_id}/playlist.m3u8"
    
    async def transcode_to_hls(
        self, 
        input_path: str, 
        video_id: int,
        on_complete: Optional[callable] = None
    ) -> dict:
        """
        Transcode video to HLS format using FFmpeg.
        
        Args:
            input_path: Path to the source video file
            video_id: Database ID of the video
            on_complete: Optional callback when transcoding completes
            
        Returns:
            dict with status, output_dir, playlist_path
        """
        output_dir = self.get_video_output_dir(video_id)
        os.makedirs(output_dir, exist_ok=True)
        
        playlist_path = os.path.join(output_dir, "playlist.m3u8")
        segment_pattern = os.path.join(output_dir, "segment_%03d.ts")
        
        # FFmpeg command for HLS conversion
        # Single quality, optimized for speed
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", "libx264",           # H.264 codec
            "-preset", "fast",            # Fast encoding
            "-crf", "23",                 # Quality (lower = better, 23 is default)
            "-c:a", "aac",                # AAC audio
            "-b:a", "128k",               # Audio bitrate
            "-ar", "44100",               # Audio sample rate
            "-ac", "2",                   # Stereo audio
            "-f", "hls",                  # HLS format
            "-hls_time", str(HLS_SEGMENT_DURATION),
            "-hls_playlist_type", HLS_PLAYLIST_TYPE,
            "-hls_segment_filename", segment_pattern,
            "-y",                         # Overwrite output
            playlist_path
        ]
        
        logger.info(f"Starting HLS transcoding for video {video_id}")
        logger.debug(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")
        
        try:
            # Run FFmpeg asynchronously
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"FFmpeg failed for video {video_id}: {error_msg}")
                return {
                    "status": "failed",
                    "error": error_msg,
                    "video_id": video_id
                }
            
            # Verify output exists
            if not os.path.exists(playlist_path):
                logger.error(f"Playlist not created for video {video_id}")
                return {
                    "status": "failed",
                    "error": "Playlist file not created",
                    "video_id": video_id
                }
            
            logger.info(f"HLS transcoding completed for video {video_id}")
            
            result = {
                "status": "ready",
                "video_id": video_id,
                "output_dir": output_dir,
                "playlist_path": playlist_path,
                "playlist_url": self.get_playlist_url(video_id)
            }
            
            if on_complete:
                await on_complete(result)
            
            return result
            
        except Exception as e:
            logger.exception(f"Error transcoding video {video_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "video_id": video_id
            }
    
    async def generate_thumbnail(
        self, 
        input_path: str, 
        video_id: int,
        timestamp: str = "00:00:01"
    ) -> Optional[str]:
        """
        Generate a thumbnail image from the video.
        
        Args:
            input_path: Path to the source video
            video_id: Database ID of the video
            timestamp: Time position for thumbnail (default: 1 second)
            
        Returns:
            Path to the thumbnail or None if failed
        """
        output_dir = self.get_video_output_dir(video_id)
        os.makedirs(output_dir, exist_ok=True)
        
        thumbnail_path = os.path.join(output_dir, "thumbnail.jpg")
        
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ss", timestamp,
            "-vframes", "1",
            "-vf", "scale=320:-1",  # 320px width, maintain aspect ratio
            "-y",
            thumbnail_path
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode == 0 and os.path.exists(thumbnail_path):
                logger.info(f"Thumbnail generated for video {video_id}")
                return thumbnail_path
            else:
                logger.warning(f"Failed to generate thumbnail for video {video_id}")
                return None
                
        except Exception as e:
            logger.exception(f"Error generating thumbnail for video {video_id}: {e}")
            return None
    
    def delete_hls_files(self, video_id: int) -> bool:
        """
        Delete all HLS files for a video.
        
        Args:
            video_id: Database ID of the video
            
        Returns:
            True if deleted successfully
        """
        output_dir = self.get_video_output_dir(video_id)
        
        if not os.path.exists(output_dir):
            return True
        
        try:
            import shutil
            shutil.rmtree(output_dir)
            logger.info(f"Deleted HLS files for video {video_id}")
            return True
        except Exception as e:
            logger.exception(f"Error deleting HLS files for video {video_id}: {e}")
            return False
    
    def get_processing_status(self, video_id: int) -> dict:
        """
        Check the processing status of a video.
        
        Args:
            video_id: Database ID of the video
            
        Returns:
            dict with status information
        """
        output_dir = self.get_video_output_dir(video_id)
        playlist_path = self.get_playlist_path(video_id)
        
        if not os.path.exists(output_dir):
            return {"status": "pending", "video_id": video_id}
        
        if os.path.exists(playlist_path):
            # Count segments
            segments = [f for f in os.listdir(output_dir) if f.endswith('.ts')]
            return {
                "status": "ready",
                "video_id": video_id,
                "segments_count": len(segments),
                "playlist_url": self.get_playlist_url(video_id)
            }
        
        return {"status": "processing", "video_id": video_id}


# Singleton instance
hls_processor = HLSProcessor()


async def process_video_background(
    input_path: str,
    video_id: int,
    db_session_factory,
    cleanup_source: bool = True
):
    """
    Background task to process video to HLS format.
    Updates the database when complete.
    
    Args:
        input_path: Path to the source video file
        video_id: Database ID of the video
        db_session_factory: SQLAlchemy session factory
        cleanup_source: Whether to delete the source file after processing
    """
    from app.models.video import Video
    
    logger.info(f"Background processing started for video {video_id}")
    
    # Update status to processing
    db = db_session_factory()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.processing_status = "processing"
            db.commit()
    except Exception as e:
        logger.error(f"Error updating video status: {e}")
    finally:
        db.close()
    
    # Check if input_path exists locally, if not try to download from S3
    local_input = input_path
    downloaded_temp = False
    
    if not os.path.exists(input_path):
        import tempfile
        from app.core.aws import s3_client, settings, HAS_AWS_CREDENTIALS
        
        if not HAS_AWS_CREDENTIALS:
             logger.error(f"File not found locally and no AWS credentials: {input_path}")
             # Fail the video processing
             db = db_session_factory()
             try:
                 video = db.query(Video).filter(Video.id == video_id).first()
                 if video:
                     video.processing_status = "failed"
                     video.error_message = "File not found locally"
                     db.commit()
             finally:
                 db.close()
             return

        logger.info(f"File not found locally: {input_path}. Attempting S3 download...")
        
        try:
            # Create temp file
            suffix = os.path.splitext(input_path)[1] or '.mp4'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                local_input = tmp.name
            
            # Download
            s3_client.download_file(settings.S3_BUCKET_NAME, input_path, local_input)
            downloaded_temp = True
            logger.info(f"Downloaded S3 key {input_path} to {local_input}")
            
        except Exception as e:
            logger.error(f"Failed to download from S3: {e}")
            # Fail the video processing
            db = db_session_factory()
            try:
                video = db.query(Video).filter(Video.id == video_id).first()
                if video:
                    video.processing_status = "failed"
                    db.commit()
            finally:
                db.close()
            return

    try:
        # Transcode to HLS
        result = await hls_processor.transcode_to_hls(local_input, video_id)
        
        # Generate thumbnail
        thumbnail_path = await hls_processor.generate_thumbnail(local_input, video_id)
        
        # Update database with results
        db = db_session_factory()
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                video.processing_status = result["status"]
                if result["status"] == "ready":
                    video.hls_path = result["playlist_url"]
                if thumbnail_path:
                    video.thumbnail_path = f"/hls/{video_id}/thumbnail.jpg"
                db.commit()
                logger.info(f"Video {video_id} processing complete: {result['status']}")
        except Exception as e:
            logger.error(f"Error updating video after processing: {e}")
        finally:
            db.close()
            
    finally:
        # Cleanup temp file if we downloaded it
        if downloaded_temp and os.path.exists(local_input):
            try:
                os.remove(local_input)
                logger.info(f"Cleaned up temp S3 download: {local_input}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")
        
        # Cleanup source file if requested AND it was a local original (not S3 download)
        if cleanup_source and not downloaded_temp and os.path.exists(input_path):
            try:
                os.remove(input_path)
                logger.info(f"Cleaned up source file: {input_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup source file: {e}")
