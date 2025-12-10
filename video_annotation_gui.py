#!/usr/bin/env python3
"""
Video Annotation GUI Application
Allows users to load videos, navigate through frames, and create timestamped annotations.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import cv2
from PIL import Image, ImageTk

from video_player import VideoPlayer
from annotation_manager import AnnotationManager
from gui_builder import GUIBuilder


class VideoAnnotationApp:
    """Main application controller"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Video Annotation Tool")
        
        # Start in fullscreen
        self.root.attributes('-zoomed', True)  # Maximize window on Linux
        
        # Apply modern theme
        self._setup_modern_theme()
        
        # Initialize components
        self.player = VideoPlayer()
        self.annotation_mgr = AnnotationManager()
        self.gui_builder = GUIBuilder(root)
        
        # Playback state
        self.is_playing = False
        self.playback_id = None
        self.photo = None  # Keep reference to prevent garbage collection
        
        # Build GUI and connect events
        self.widgets = self.gui_builder.build_gui()
        self._connect_events()
    
    def _setup_modern_theme(self):
        """Setup modern color scheme and styling"""
        # Configure ttk style
        style = ttk.Style()
        
        # Try to use a modern theme if available
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Modern color palette
        bg_color = "#1e1e1e"  # Dark background
        fg_color = "#e0e0e0"  # Light text
        accent_color = "#007acc"  # Blue accent
        secondary_bg = "#2d2d2d"  # Slightly lighter background
        button_bg = "#0e639c"  # Button color
        button_hover = "#1177bb"  # Button hover
        
        # Configure root window
        self.root.configure(bg=bg_color)
        
        # Configure styles
        style.configure(".", background=bg_color, foreground=fg_color)
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        style.configure("TLabelframe", background=bg_color, foreground=fg_color, borderwidth=0)
        style.configure("TLabelframe.Label", background=bg_color, foreground=accent_color, font=("Segoe UI", 11, "bold"))
        
        # Button styles
        style.configure("TButton", 
                       background=button_bg, 
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none",
                       font=("Segoe UI", 10))
        style.map("TButton",
                 background=[("active", button_hover), ("pressed", accent_color)])
        
        # Accent button style
        style.configure("Accent.TButton",
                       background=accent_color,
                       foreground="white",
                       borderwidth=0,
                       font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton",
                 background=[("active", button_hover), ("pressed", "#005a9e")])
        
        # Entry and Combobox
        style.configure("TEntry", fieldbackground=secondary_bg, foreground=fg_color, borderwidth=1)
        style.configure("TCombobox", fieldbackground=secondary_bg, foreground=fg_color, borderwidth=1)
        style.map("TCombobox", fieldbackground=[("readonly", secondary_bg)])
        
        # Scale (slider)
        style.configure("TScale", background=bg_color, troughcolor=secondary_bg, borderwidth=0)
        
    def _connect_events(self):
        """Connect UI events to handlers"""
        # File controls
        self.widgets['load_btn'].config(command=self.load_video)
        self.widgets['annot_dir_btn'].config(command=self.set_annotation_dir)
        
        # Playback controls
        self.widgets['play_btn'].config(command=self.toggle_playback)
        
        # Frame navigation
        self.widgets['prev_frame_btn'].config(command=self.previous_frame)
        self.widgets['next_frame_btn'].config(command=self.next_frame)
        
        # Time skip controls
        self.widgets['skip_30s_back_btn'].config(command=lambda: self.skip_time(-30))
        self.widgets['skip_5s_back_btn'].config(command=lambda: self.skip_time(-5))
        self.widgets['skip_1s_back_btn'].config(command=lambda: self.skip_time(-1))
        self.widgets['skip_1s_fwd_btn'].config(command=lambda: self.skip_time(1))
        self.widgets['skip_5s_fwd_btn'].config(command=lambda: self.skip_time(5))
        self.widgets['skip_30s_fwd_btn'].config(command=lambda: self.skip_time(30))
        
        # Annotation controls
        self.widgets['start_btn'].config(command=self.mark_start)
        self.widgets['end_btn'].config(command=self.mark_end_and_save)
        self.widgets['clear_btn'].config(command=self.clear_markers)
        self.widgets['annotation_combo'].bind("<<ComboboxSelected>>", self.on_history_selected)
        
        # Navigation bar
        self.widgets['nav_scale'].config(command=self.on_nav_scale_change)
        self.is_nav_scale_drag = False
        self.widgets['nav_scale'].bind("<Button-1>", self.on_nav_scale_click)
    
    def load_video(self):
        """Load a video file"""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.mts *.tiff *.tif"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        success, error = self.player.load_video(file_path)
        
        if not success:
            messagebox.showerror("Error", error)
            return
        
        # Update UI
        self.widgets['file_label'].config(text=os.path.basename(file_path))
        self.widgets['nav_scale'].config(to=self.player.total_frames - 1)
        self.display_frame()
        self.update_status(f"Video loaded: {self.player.total_frames} frames at {self.player.fps:.2f} fps")
    
    def display_frame(self):
        """Display the current frame on the canvas"""
        if not self.player.is_loaded():
            return
        
        success, frame, used_cache = self.player.get_frame()
        
        if not success:
            return
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize frame to fit canvas
        canvas = self.widgets['canvas']
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 800
            canvas_height = 450
        
        # Calculate scaling
        scale_w = canvas_width / self.player.frame_width
        scale_h = canvas_height / self.player.frame_height
        scale = min(scale_w, scale_h)
        
        new_width = int(self.player.frame_width * scale)
        new_height = int(self.player.frame_height * scale)
        
        # Resize frame
        frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
        
        # Convert to PIL Image
        img = Image.fromarray(frame_resized)
        self.photo = ImageTk.PhotoImage(image=img)
        
        # Display on canvas
        canvas.delete("all")
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
        
        # Update timestamp and frame info
        self.update_timestamp_display()
        self.update_nav_scale()
        
        if used_cache:
            self.update_status("Warning: Using cached frame (decode error)")
    
    def update_timestamp_display(self):
        """Update the timestamp and frame number display"""
        if not self.player.is_loaded():
            return
        
        timestamp_seconds = self.player.get_current_timestamp()
        timestamp_str = self.player.format_timestamp(timestamp_seconds)
        
        self.widgets['timestamp_label'].config(text=timestamp_str)
        self.widgets['frame_label'].config(text=f"{self.player.current_frame} / {self.player.total_frames}")
    
    def update_nav_scale(self):
        """Update navigation bar position without triggering callback"""
        if not self.player.is_loaded():
            return
        
        # Only update if not being dragged by user
        if not self.is_nav_scale_drag:
            self.widgets['nav_scale'].set(self.player.current_frame)
    
    def on_nav_scale_click(self, event):
        """Handle navigation bar click or drag"""
        if not self.player.is_loaded():
            return
        
        # Remember if we were playing
        was_playing = self.is_playing
        
        # Pause playback if playing
        if self.is_playing:
            self.toggle_playback()
        
        # Mark as dragging
        self.is_nav_scale_drag = True
        
        # Calculate frame from click position
        scale_widget = self.widgets['nav_scale']
        scale_width = scale_widget.winfo_width()
        click_x = event.x
        
        # Calculate the frame number based on click position
        if scale_width > 0:
            frame_num = int((click_x / scale_width) * self.player.total_frames)
            frame_num = max(0, min(frame_num, self.player.total_frames - 1))
            
            # Update player and display
            self.player.current_frame = frame_num
            self.display_frame()
        
        # Store playing state for release
        self.was_playing_before_nav = was_playing
        
        # Bind drag and release events
        scale_widget.bind("<B1-Motion>", self.on_nav_scale_drag)
        scale_widget.bind("<ButtonRelease-1>", self.on_nav_scale_release)
    
    def on_nav_scale_drag(self, event):
        """Handle navigation bar dragging"""
        if not self.player.is_loaded():
            return
        
        scale_widget = self.widgets['nav_scale']
        scale_width = scale_widget.winfo_width()
        drag_x = event.x
        
        # Calculate the frame number based on drag position
        if scale_width > 0:
            frame_num = int((drag_x / scale_width) * self.player.total_frames)
            frame_num = max(0, min(frame_num, self.player.total_frames - 1))
            
            # Update player and display
            if frame_num != self.player.current_frame:
                self.player.current_frame = frame_num
                self.display_frame()
    
    def on_nav_scale_release(self, event):
        """Handle navigation bar release"""
        self.is_nav_scale_drag = False
        
        # Resume playback if it was playing before
        if hasattr(self, 'was_playing_before_nav') and self.was_playing_before_nav:
            if not self.is_playing:
                self.toggle_playback()
        
        # Unbind drag events
        self.widgets['nav_scale'].unbind("<B1-Motion>")
        self.widgets['nav_scale'].unbind("<ButtonRelease-1>")
    
    def on_nav_scale_change(self, value):
        """Handle navigation bar position change"""
        # This callback is no longer used for seeking
        pass
    
    def toggle_playback(self):
        """Toggle video playback"""
        if not self.player.is_loaded():
            return
        
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.widgets['play_btn'].config(text="⏸ Pause")
            self.play_video()
        else:
            self.widgets['play_btn'].config(text="▶ Play")
            if self.playback_id is not None:
                self.root.after_cancel(self.playback_id)
                self.playback_id = None
    
    def play_video(self):
        """Continuously play video frames"""
        if not self.is_playing:
            return
        
        if self.player.next_frame():
            self.display_frame()
            
            # Calculate delay based on fps
            delay = int(1000 / self.player.fps) if self.player.fps > 0 else 33
            self.playback_id = self.root.after(delay, self.play_video)
        else:
            # Reached end of video
            self.is_playing = False
            self.widgets['play_btn'].config(text="▶ Play")
            self.playback_id = None
    
    def next_frame(self):
        """Go to next frame"""
        if not self.player.is_loaded():
            return
        
        # Pause playback if playing
        if self.is_playing:
            self.toggle_playback()
        
        self.player.next_frame()
        self.display_frame()
    
    def previous_frame(self):
        """Go to previous frame"""
        if not self.player.is_loaded():
            return
        
        # Pause playback if playing
        if self.is_playing:
            self.toggle_playback()
        
        self.player.previous_frame()
        self.display_frame()
    
    def skip_time(self, seconds):
        """Skip forward or backward by specified seconds"""
        if not self.player.is_loaded():
            return
        
        # Pause playback if playing
        if self.is_playing:
            self.toggle_playback()
        
        self.player.skip_time(seconds)
        self.display_frame()
    
    def set_annotation_dir(self):
        """Set custom directory for saving annotations"""
        directory = filedialog.askdirectory(
            title="Select Annotation Directory",
            initialdir=self.annotation_mgr.get_directory() or os.path.expanduser("~")
        )
        
        if directory:
            self.annotation_mgr.set_directory(directory)
            # Show shortened path
            if len(directory) > 50:
                display_path = "..." + directory[-47:]
            else:
                display_path = directory
            self.widgets['annot_dir_label'].config(text=display_path, foreground="#51cf66")
            self.update_status(f"Annotation directory set to: {directory}")
    
    def mark_start(self):
        """Mark the start timestamp"""
        if not self.player.is_loaded():
            messagebox.showwarning("Warning", "Please load a video first")
            return
        
        timestamp = self.player.get_current_timestamp()
        self.annotation_mgr.set_start(timestamp)
        timestamp_str = self.player.format_timestamp(timestamp)
        self.widgets['start_label'].config(text=timestamp_str, foreground="#51cf66")
        self.update_status(f"Start marked at {timestamp_str}")
    
    def mark_end_and_save(self):
        """Mark the end timestamp and save annotation"""
        if not self.player.is_loaded():
            messagebox.showwarning("Warning", "Please load a video first")
            return
        
        if not self.annotation_mgr.has_start():
            messagebox.showwarning("Warning", "Please mark start timestamp first")
            return
        
        annotation_text = self.widgets['annotation_entry'].get().strip()
        if not annotation_text:
            messagebox.showwarning("Warning", "Please enter an annotation")
            return
        
        end_timestamp = self.player.get_current_timestamp()
        start_timestamp = self.annotation_mgr.get_start()
        
        # Check if end is after start
        if end_timestamp < start_timestamp:
            messagebox.showwarning("Warning", "End timestamp must be after start timestamp")
            return
        
        # Format timestamps
        start_str = self.player.format_timestamp(start_timestamp)
        end_str = self.player.format_timestamp(end_timestamp)
        
        # Save to file
        success, file_path, error = self.annotation_mgr.save_annotation(
            self.player.video_path, start_str, end_str, annotation_text
        )
        
        if not success:
            messagebox.showerror("Error", f"Failed to save annotation: {error}")
            return
        
        # Update annotation history
        self.annotation_mgr.add_to_history(annotation_text)
        self.widgets['annotation_combo']['values'] = self.annotation_mgr.get_history()
        
        # Update UI
        self.widgets['end_label'].config(text=end_str, foreground="#51cf66")
        self.update_status(f"Annotation saved: {start_str} to {end_str}")
        
        # Show success and clear for next annotation
        messagebox.showinfo("Success", f"Annotation saved to:\n{file_path}")
        self.widgets['annotation_entry'].delete(0, tk.END)
    
    def clear_markers(self):
        """Clear start and end markers"""
        self.annotation_mgr.clear_start()
        self.widgets['start_label'].config(text="Not set", foreground="#ff6b6b")
        self.widgets['end_label'].config(text="Not set", foreground="#ff6b6b")
        self.update_status("Markers cleared")
    
    def on_history_selected(self, event):
        """Handle annotation history selection"""
        selected = self.widgets['annotation_combo'].get()
        if selected:
            self.widgets['annotation_entry'].delete(0, tk.END)
            self.widgets['annotation_entry'].insert(0, selected)
    
    def update_status(self, message):
        """Update status bar"""
        self.widgets['status_bar'].config(text=message)
    
    def cleanup(self):
        """Cleanup resources"""
        # Stop playback
        if self.is_playing:
            self.is_playing = False
        if self.playback_id is not None:
            self.root.after_cancel(self.playback_id)
        
        # Release video
        self.player.release()


def main():
    root = tk.Tk()
    app = VideoAnnotationApp(root)
    
    # Handle window close
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
