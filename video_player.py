"""
Video Player Module
Handles video loading, frame reading, and playback control
"""

import cv2
from datetime import timedelta


class VideoPlayer:
    """Manages video file operations and frame navigation"""
    
    def __init__(self):
        self.video_capture = None
        self.video_path = None
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 0
        self.frame_width = 0
        self.frame_height = 0
        self.last_valid_frame = None
        self.last_read_position = -1
        
    def load_video(self, file_path):
        """
        Load a video file
        Returns: tuple (success: bool, error_message: str or None)
        """
        # Release previous video if any
        if self.video_capture is not None:
            self.video_capture.release()
        
        # Open new video with backend that handles H264 better
        self.video_capture = cv2.VideoCapture(file_path, cv2.CAP_FFMPEG)
        
        if not self.video_capture.isOpened():
            # Fallback to default backend
            self.video_capture = cv2.VideoCapture(file_path)
        
        if not self.video_capture.isOpened():
            return False, "Failed to open video file"
        
        # Get video properties
        self.video_path = file_path
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.frame_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Reset state
        self.current_frame = 0
        self.last_valid_frame = None
        self.last_read_position = -1
        
        return True, None
    
    def get_frame(self):
        """
        Get the current frame
        Returns: tuple (success: bool, frame: numpy array or None, used_cache: bool)
        """
        if self.video_capture is None:
            return False, None, False
        
        # For sequential frame access, read sequentially
        if abs(self.current_frame - self.last_read_position) == 1:
            if self.current_frame > self.last_read_position:
                # Moving forward - just read next
                ret, frame = self.video_capture.read()
            else:
                # Moving backward - need to seek
                ret, frame = self._seek_and_read()
        else:
            # Non-sequential access - need to seek
            ret, frame = self._seek_and_read()
        
        if not ret or frame is None:
            # Use last valid frame if available
            if self.last_valid_frame is not None:
                frame = self.last_valid_frame.copy()
                return True, frame, True  # Indicate we used cache
            else:
                return False, None, False
        else:
            # Cache this valid frame
            self.last_valid_frame = frame.copy()
            self.last_read_position = self.current_frame
            return True, frame, False
    
    def _seek_and_read(self):
        """Helper method to seek and read frame with error recovery"""
        # Try direct seek
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.video_capture.read()
        
        if ret:
            return ret, frame
        
        # If direct seek fails, try seeking back to keyframe and reading forward
        keyframe_interval = 30  # Typical GOP size
        seek_back = min(self.current_frame, keyframe_interval)
        
        if seek_back > 0:
            start_frame = self.current_frame - seek_back
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            # Read forward to target frame
            for i in range(seek_back + 1):
                ret, frame = self.video_capture.read()
                if not ret:
                    break
            
            if ret:
                return ret, frame
        
        return False, None
    
    def next_frame(self):
        """Move to next frame"""
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            return True
        return False
    
    def previous_frame(self):
        """Move to previous frame"""
        if self.current_frame > 0:
            self.current_frame -= 1
            return True
        return False
    
    def skip_frames(self, frame_count):
        """
        Skip forward or backward by frame count
        Returns: actual frames skipped
        """
        new_frame = self.current_frame + frame_count
        new_frame = max(0, min(new_frame, self.total_frames - 1))
        old_frame = self.current_frame
        self.current_frame = new_frame
        return new_frame - old_frame
    
    def skip_time(self, seconds):
        """
        Skip forward or backward by seconds
        Returns: actual frames skipped
        """
        frames_to_skip = int(seconds * self.fps)
        return self.skip_frames(frames_to_skip)
    
    def get_current_timestamp(self):
        """Get current timestamp in seconds"""
        return self.current_frame / self.fps if self.fps > 0 else 0
    
    def format_timestamp(self, seconds):
        """Format seconds to HH:MM:SS.mmm"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = td.total_seconds() % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    
    def is_loaded(self):
        """Check if a video is loaded"""
        return self.video_capture is not None
    
    def release(self):
        """Release video resources"""
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
