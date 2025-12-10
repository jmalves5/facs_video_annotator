"""
GUI Builder Module
Constructs the user interface components
"""

import tkinter as tk
from tkinter import ttk


class GUIBuilder:
    """Builds and manages GUI components"""
    
    def __init__(self, root):
        self.root = root
        self.widgets = {}
        
    def build_gui(self):
        """Build the complete GUI and return widget dictionary"""
        # Main container with dark theme
        main_container = ttk.Frame(self.root, padding="15")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Build sections
        self._build_file_section(main_container)
        self._build_video_section(main_container)
        self._build_navigation_section(main_container)
        self._build_annotation_section(main_container)
        self._build_status_bar(main_container)
        
        return self.widgets
    
    def _build_file_section(self, parent):
        """Build file controls section"""
        file_frame = ttk.LabelFrame(parent, text="Video File", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        self.widgets['file_label'] = ttk.Label(file_frame, text="No video loaded", 
                                               font=("Arial", 11))
        self.widgets['file_label'].grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.widgets['load_btn'] = ttk.Button(file_frame, text="📁 Load Video", width=15)
        self.widgets['load_btn'].grid(row=0, column=1, padx=5)
        
        # Annotation directory
        ttk.Label(file_frame, text="Annotations:", 
                 font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=(10, 0))
        self.widgets['annot_dir_label'] = ttk.Label(file_frame, text="Same as video", 
                                                     font=("Arial", 10, "italic"))
        self.widgets['annot_dir_label'].grid(row=2, column=0, sticky=tk.W, padx=5)
        
        self.widgets['annot_dir_btn'] = ttk.Button(file_frame, text="📂 Set Directory", width=15)
        self.widgets['annot_dir_btn'].grid(row=1, column=1, rowspan=2, padx=5)
    
    def _build_video_section(self, parent):
        """Build video display section"""
        video_frame = ttk.LabelFrame(parent, text="Video Display", padding="10")
        video_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=0)
        
        # Canvas for video display with 16:9 aspect ratio by default
        # Will be adjusted based on actual video aspect ratio when loaded
        default_width = 960
        default_height = 540  # 16:9 aspect ratio
        self.widgets['canvas'] = tk.Canvas(video_frame, bg="#2d2d2d", 
                                          width=default_width, height=default_height,
                                          highlightthickness=0, relief=tk.FLAT)
        self.widgets['canvas'].grid(row=0, column=0, pady=(0, 10))
        
        # Navigation bar (scrubber) with modern styling
        nav_bar_frame = ttk.Frame(video_frame)
        nav_bar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        nav_bar_frame.columnconfigure(0, weight=1)
        
        self.widgets['nav_scale'] = tk.Scale(
            nav_bar_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            showvalue=False,
            relief=tk.FLAT,
            length=800,
            bg="#007acc",
            fg="#007acc",
            troughcolor="#1e1e1e",
            activebackground="#1177bb",
            highlightthickness=0,
            sliderrelief=tk.FLAT,
            width=15
        )
        self.widgets['nav_scale'].grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10)
        
        # Timestamp display with modern styling
        timestamp_frame = ttk.Frame(video_frame)
        timestamp_frame.grid(row=2, column=0, pady=(5, 0))
        
        ttk.Label(timestamp_frame, text="Current Timestamp:", 
                 font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.widgets['timestamp_label'] = ttk.Label(timestamp_frame, text="00:00:00.000", 
                                                     font=("Arial", 18, "bold"),
                                                     foreground="#007acc")
        self.widgets['timestamp_label'].grid(row=0, column=1, padx=5)
        
        ttk.Label(timestamp_frame, text="Frame:", 
                 font=("Arial", 10)).grid(row=0, column=2, padx=(20, 5))
        self.widgets['frame_label'] = ttk.Label(timestamp_frame, text="0 / 0", 
                                                font=("Arial", 14))
        self.widgets['frame_label'].grid(row=0, column=3, padx=5)
    
    def _build_navigation_section(self, parent):
        """Build navigation controls section"""
        nav_frame = ttk.LabelFrame(parent, text="Navigation Controls", padding="10")
        nav_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Playback controls
        playback_nav = ttk.Frame(nav_frame)
        playback_nav.grid(row=0, column=0, pady=(0, 8))
        
        ttk.Label(playback_nav, text="Playback:", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, padx=(0, 10))
        self.widgets['play_btn'] = ttk.Button(playback_nav, text="▶ Play", width=14, 
                                             style="Accent.TButton")
        self.widgets['play_btn'].grid(row=0, column=1, padx=2)
        
        # Frame navigation
        frame_nav = ttk.Frame(nav_frame)
        frame_nav.grid(row=1, column=0, pady=(0, 8))
        
        ttk.Label(frame_nav, text="Frame:", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, padx=(0, 10))
        self.widgets['prev_frame_btn'] = ttk.Button(frame_nav, text="◄ Previous", width=12)
        self.widgets['prev_frame_btn'].grid(row=0, column=1, padx=2)
        self.widgets['next_frame_btn'] = ttk.Button(frame_nav, text="Next ►", width=12)
        self.widgets['next_frame_btn'].grid(row=0, column=2, padx=2)
        
        # Time skip navigation
        time_nav = ttk.Frame(nav_frame)
        time_nav.grid(row=2, column=0, pady=0)
        
        ttk.Label(time_nav, text="Skip:", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, padx=(0, 10))
        self.widgets['skip_30s_back_btn'] = ttk.Button(time_nav, text="<< 30s", width=8)
        self.widgets['skip_30s_back_btn'].grid(row=0, column=1, padx=2)
        self.widgets['skip_5s_back_btn'] = ttk.Button(time_nav, text="< 5s", width=8)
        self.widgets['skip_5s_back_btn'].grid(row=0, column=2, padx=2)
        self.widgets['skip_1s_back_btn'] = ttk.Button(time_nav, text="< 1s", width=8)
        self.widgets['skip_1s_back_btn'].grid(row=0, column=3, padx=2)
        self.widgets['skip_1s_fwd_btn'] = ttk.Button(time_nav, text="1s >", width=8)
        self.widgets['skip_1s_fwd_btn'].grid(row=0, column=4, padx=2)
        self.widgets['skip_5s_fwd_btn'] = ttk.Button(time_nav, text="5s >", width=8)
        self.widgets['skip_5s_fwd_btn'].grid(row=0, column=5, padx=2)
        self.widgets['skip_30s_fwd_btn'] = ttk.Button(time_nav, text="30s >>", width=8)
        self.widgets['skip_30s_fwd_btn'].grid(row=0, column=6, padx=2)
    
    def _build_annotation_section(self, parent):
        """Build annotation section"""
        annotation_frame = ttk.LabelFrame(parent, text="Annotation", padding="10")
        annotation_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        annotation_frame.columnconfigure(1, weight=1)
        
        # Annotation entry
        ttk.Label(annotation_frame, text="Annotation:", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5, sticky=tk.W)
        self.widgets['annotation_entry'] = ttk.Entry(annotation_frame, width=50, 
                                                     font=("Arial", 11))
        self.widgets['annotation_entry'].grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E), pady=5)
        
        # Annotation history dropdown
        ttk.Label(annotation_frame, text="Recent:", 
                 font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.widgets['annotation_combo'] = ttk.Combobox(annotation_frame, width=30, 
                                                       state="readonly", font=("Arial", 10))
        self.widgets['annotation_combo'].grid(row=0, column=3, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(annotation_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=15)
        
        self.widgets['start_btn'] = ttk.Button(button_frame, text="⏱ Start Here", 
                                              style="Accent.TButton", width=15)
        self.widgets['start_btn'].grid(row=0, column=0, padx=5)
        
        self.widgets['end_btn'] = ttk.Button(button_frame, text="💾 End/Save Here", 
                                            style="Accent.TButton", width=15)
        self.widgets['end_btn'].grid(row=0, column=1, padx=5)
        
        self.widgets['clear_btn'] = ttk.Button(button_frame, text="🗑 Clear", width=12)
        self.widgets['clear_btn'].grid(row=0, column=2, padx=5)
        
        # Status display with modern styling
        status_frame = ttk.Frame(annotation_frame)
        status_frame.grid(row=2, column=0, columnspan=4, pady=(5, 0))
        
        ttk.Label(status_frame, text="Start:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, padx=(0, 5))
        self.widgets['start_label'] = ttk.Label(status_frame, text="Not set", 
                                               font=("Arial", 13, "bold"), 
                                               foreground="#ff6b6b")
        self.widgets['start_label'].grid(row=0, column=1, padx=5)
        
        ttk.Label(status_frame, text="End:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=2, padx=(20, 5))
        self.widgets['end_label'] = ttk.Label(status_frame, text="Not set", 
                                             font=("Arial", 13, "bold"), 
                                             foreground="#ff6b6b")
        self.widgets['end_label'].grid(row=0, column=3, padx=5)
    
    def _build_status_bar(self, parent):
        """Build status bar"""
        self.widgets['status_bar'] = ttk.Label(parent, text="Ready", relief=tk.FLAT,
                                              font=("Arial", 10), padding=5)
        self.widgets['status_bar'].grid(row=4, column=0, sticky=(tk.W, tk.E))
