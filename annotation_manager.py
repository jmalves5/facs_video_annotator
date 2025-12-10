"""
Annotation Manager Module
Handles annotation storage and file operations
"""

import os


class AnnotationManager:
    """Manages annotations and saving to file"""
    
    def __init__(self):
        self.start_timestamp = None
        self.annotation_history = []
        self.annotation_dir = None
        
    def set_start(self, timestamp):
        """Set the start timestamp"""
        self.start_timestamp = timestamp
    
    def clear_start(self):
        """Clear the start timestamp"""
        self.start_timestamp = None
    
    def has_start(self):
        """Check if start timestamp is set"""
        return self.start_timestamp is not None
    
    def get_start(self):
        """Get the start timestamp"""
        return self.start_timestamp
    
    def add_to_history(self, annotation):
        """Add annotation to history if not already present"""
        if annotation and annotation not in self.annotation_history:
            self.annotation_history.append(annotation)
    
    def get_history(self):
        """Get annotation history"""
        return self.annotation_history
    
    def set_directory(self, directory):
        """Set custom annotation directory"""
        self.annotation_dir = directory
    
    def get_directory(self):
        """Get current annotation directory"""
        return self.annotation_dir
    
    def save_annotation(self, video_path, start_time_str, end_time_str, annotation_text):
        """
        Save annotation to file
        Returns: tuple (success: bool, file_path: str or None, error_message: str or None)
        """
        if not video_path:
            return False, None, "No video loaded"
        
        # Determine annotation directory
        if self.annotation_dir:
            annot_dir = self.annotation_dir
        else:
            annot_dir = os.path.dirname(video_path)
        
        # Create annotation filename - use single file for all annotations
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        annotation_file = os.path.join(annot_dir, f"{video_name}_annotations.txt")
        
        # Determine video path format (relative if in home, absolute otherwise)
        home_dir = os.path.expanduser("~")
        abs_video_path = os.path.abspath(video_path)
        
        if abs_video_path.startswith(home_dir):
            # Use relative path from home
            video_path_str = os.path.relpath(abs_video_path, home_dir)
        else:
            # Use absolute path
            video_path_str = abs_video_path
        
        try:
            # Append annotation
            with open(annotation_file, 'a', encoding='utf-8') as f:
                f.write(f"{video_path_str}\t{start_time_str}\t{end_time_str}\t{annotation_text}\n")
            
            return True, annotation_file, None
        except Exception as e:
            return False, None, str(e)
