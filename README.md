# Video Annotation GUI

A simple and intuitive GUI application for annotating videos with timestamps.

## Features

- **Video Playback**: Load and display video files
- **Frame Navigation**: Navigate frame-by-frame with Previous/Next buttons
- **Time Skip Controls**: Skip by 1s, 5s, or 30s in either direction
- **Timestamp Display**: Real-time display of current timestamp and frame number
- **Annotation System**: 
  - Text entry field for annotations
  - History dropdown with recently used annotations
  - Mark start and end timestamps
  - Save annotations to text file
- **Clear Function**: Reset start/end markers

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python video_annotation_gui.py
```

2. Click "Load Video" to select a video file
3. Navigate through the video using:
   - Frame controls: Previous Frame / Next Frame
   - Time skip: -30s, -5s, -1s, +1s, +5s, +30s
4. To create an annotation:
   - Navigate to the start point
   - Click "Start Here"
   - Navigate to the end point
   - Enter annotation text
   - Click "End/Save Here"
5. Annotations are saved to `{video_name}_annotations.txt` in the same directory as the video

## Output Format

Annotations are saved in tab-separated format:
```
START_TIME    END_TIME    ANNOTATION
00:00:05.000  00:00:10.500  Example annotation
```

## Keyboard Shortcuts

Currently all controls are button-based. You can extend the application to add keyboard shortcuts if needed.
# facs_video_annotator
