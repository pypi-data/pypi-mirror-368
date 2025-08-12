import cv2
import subprocess
import logging
import json
import fractions
import shutil
from urllib.parse import urlparse

class VideoProbeUtil:
    """Utility to extract metadata from video URLs using OpenCV and ffmpeg."""
    
    @staticmethod
    def get_video_metadata(video_url: str) -> dict:
        """Extracts resolution and frame rate from a video URL using OpenCV or ffmpeg."""
        try:
            # metadata = VideoProbeUtil._get_metadata_opencv(video_url)
            metadata = VideoProbeUtil._get_metadata_ffmpeg(video_url)
            return metadata
        
        except Exception as e:
            logging.error(f"🚨 [APP] Error probing video {video_url}: {e}", exc_info=True)
            return None

    @staticmethod
    def _get_metadata_opencv(video_url: str) -> dict:
        cap = cv2.VideoCapture(video_url)
        if not cap.isOpened():
            logging.warning(f"⚠️ [APP] OpenCV failed to open video: {video_url}")
            return None

        # Read first frame to ensure the video is valid
        ret, frame = cap.read()
        if not ret or frame is None:
            logging.warning(f"⚠️ [APP] OpenCV failed to read a frame from {video_url}")
            cap.release()
            return None

        height, width = frame.shape[:2]
        frame_rate = round(cap.get(cv2.CAP_PROP_FPS), 2)
        cap.release()
        
        return {
            "resolution": f"{width}x{height}" if width and height else None,
            "frame_rate": frame_rate if frame_rate > 0 else None,
            "timestamp": None
        }
    
    @staticmethod
    def _detect_stream_type(video_url: str) -> str:
        """Detect whether the URL is RTSP, local file, or other type."""
        # Convert PosixPath to string if needed
        if hasattr(video_url, '__str__'):
            video_url = str(video_url)
        
        parsed_url = urlparse(video_url)
        if parsed_url.scheme == "rtsp":
            return "rtsp"
        elif parsed_url.scheme in ["http", "https"]:
            return "http"
        else:
            return "file"
    
    @staticmethod
    def _get_metadata_ffmpeg(video_url: str) -> dict:
        # Check if ffprobe is available
        if not shutil.which("ffprobe"):
            logging.error("⚠️ [APP] ffprobe is not installed or not found in PATH.")
            return None

        # Detect stream type
        stream_type = VideoProbeUtil._detect_stream_type(video_url)
        
        # Build ffprobe command based on stream type
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", 
               "-show_entries", "stream=width,height,avg_frame_rate", "-of", "json"]
        
        # Add RTSP transport option only for RTSP streams
        if stream_type == "rtsp":
            cmd.insert(1, "-rtsp_transport")
            cmd.insert(2, "tcp")
        
        # Add the video URL
        cmd.append(video_url)

        try:
            # Run ffprobe command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            # Check for errors
            if result.returncode != 0 or not result.stdout.strip():
                logging.warning(f"⚠️ [APP] ffprobe failed for {video_url}: {result.stderr.strip()}")
                return None

            # Parse JSON output
            metadata = json.loads(result.stdout)
            streams = metadata.get("streams", [{}])[0]

            # Extract metadata
            width = streams.get("width")
            height = streams.get("height")
            avg_fps = streams.get("avg_frame_rate", "0/1")

            # Convert FPS safely
            try:
                frame_rate = round(float(fractions.Fraction(avg_fps)), 2)
            except (ValueError, ZeroDivisionError):
                frame_rate = None

            return {
                "resolution": f"{width}x{height}" if width and height else None,
                "frame_rate": frame_rate,
                "timestamp": None  # Placeholder if you need a timestamp later
            }

        except subprocess.TimeoutExpired:
            logging.warning(f"⚠️ [APP] ffprobe timeout for {video_url}")
        except json.JSONDecodeError:
            logging.error(f"❌ [APP] Failed to parse ffprobe output for {video_url}")

        return None