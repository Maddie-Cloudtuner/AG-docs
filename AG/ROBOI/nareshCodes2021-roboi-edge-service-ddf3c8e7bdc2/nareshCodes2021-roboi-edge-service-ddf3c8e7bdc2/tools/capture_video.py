import cv2
import threading
import time
import random
import os
import datetime
import numpy as np
from collections import deque
from core.visual_utils import draw_annotations
from tools import capture_image
from core.logger import get_app_logger

logger = get_app_logger("video-recorder")

class VideoRecorder:
    def __init__(self, cam_id, save_dir="data/captures", buffer_seconds=3, post_event_seconds=5, fps=15, resolution=(1280, 720), draw_on_video=True):
        """
        Args:
            cam_id: Identifier for the camera.
            save_dir: Directory to save videos.
            buffer_seconds: How many seconds of pre-alert video to keep in memory.
            post_event_seconds: How many seconds to record AFTER the alert.
            fps: Frames per second of the stream.
            resolution: Tuple (width, height).
            draw_on_video: If True, draws bounding boxes on the video frames.
        """
        self.cam_id = cam_id
        self.save_dir = save_dir
        self.buffer_seconds = buffer_seconds
        self.post_event_seconds = post_event_seconds
        self.fps = fps
        self.resolution = resolution
        self.draw_on_video = draw_on_video
        
        # Rolling buffer for pre-event frames
        self.buffer_len = int(buffer_seconds * fps)
        self.frame_buffer = deque(maxlen=self.buffer_len)
        
        # Recording state
        self.is_recording = False
        self.remaining_frames_to_record = 0
        self.active_writer = None
        self.active_filename = None
        self.lock = threading.Lock()
        
        # Snapshot state
        self.last_alert_types = []
        self.last_snapshot_time = 0
        self.snapshot_cooldown = 3.0  # Seconds between snapshot sets

    def add_frame(self, frame_copy, frame_objects=None):
        """
        Adds a frame to the buffer. If recording, writes it to the file.
        """
        with self.lock:
            # Note: We do NOT draw on 'frame_copy' here if we want clean video.
            # We store the raw frame AND the objects so we can draw them later for snapshots.
            
            # Store in buffer as tuple
            self.frame_buffer.append((frame_copy, frame_objects))

            # Handle Video Recording
            if self.is_recording:
                self.current_session_frame += 1
                if self.active_writer:
                    # Write the CLEAN frame to video
                    self.active_writer.write(frame_copy)
                
                # Check for snapshots in the post-event phase
                if self.num_snapshots_to_sample > 0 and self.snapshots_saved_in_session < self.num_snapshots_to_sample:
                    if self.current_session_frame in self.sampled_indices:
                        self.snapshots_saved_in_session += 1
                        snap_dir = os.path.join(self.save_dir, self.active_event_dir) if self.active_event_dir else self.save_dir
                        # Generate snapshot with annotations
                        self._save_snapshot(frame_copy, "dist", frame_objects, custom_dir=snap_dir)
                
                self.remaining_frames_to_record -= 1
                if self.remaining_frames_to_record <= 0:
                    self._stop_recording()
            


    def trigger_recording(self, alert_types, snapshot_sequence=True, frame_objects=None, event_dir=None, num_snapshots=0, pre_event_seconds=None, post_event_seconds=None):
        """
        Starts recording if not already recording. 
        """
        with self.lock:
            self.last_alert_types = alert_types
            self.num_snapshots_to_sample = num_snapshots
            self.current_session_frame = 0
            self.snapshots_saved_in_session = 0
            self.active_event_dir = event_dir
            current_time = time.time()

            # --- VIDEO LOGIC ---
            if self.is_recording:
                # Extend recording time
                record_post = post_event_seconds if post_event_seconds is not None else self.post_event_seconds
                self.remaining_frames_to_record = int(record_post * self.fps)
                return

            self.is_recording = True
            
            # Use provided duration or fallback to class default
            record_post = post_event_seconds if post_event_seconds is not None else self.post_event_seconds
            self.remaining_frames_to_record = int(record_post * self.fps)
            
            if event_dir:
                active_dir = os.path.join(self.save_dir, event_dir)
            else:
                active_dir = os.path.join(self.save_dir, str(self.cam_id))
                
            os.makedirs(active_dir, exist_ok=True)
            
            # Sequential numbering for videos: 1.mp4, 2.mp4, etc.
            existing_videos = [f for f in os.listdir(active_dir) if f.endswith(".mp4")]
            next_num = len(existing_videos) + 1
            filename = f"{next_num}.mp4"
            
            filepath = os.path.join(active_dir, filename)
            self.active_filename = filepath
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.active_writer = cv2.VideoWriter(
                filepath, fourcc, self.fps, self.resolution
            )
            
            if not self.active_writer.isOpened():
                logger.error(f"Failed to open video writer for {filepath}")
                self.is_recording = False
                return

            # Calculate Sampling Indices
            # Total frames = (buffer frames being written) + post_event frames
            
            # Determine how many buffer frames to write
            if pre_event_seconds is not None:
                requested_buffer_len = int(pre_event_seconds * self.fps)
                # Cap it at actual buffer size
                requested_buffer_len = min(requested_buffer_len, len(self.frame_buffer))
            else:
                requested_buffer_len = len(self.frame_buffer)
            
            total_expected_frames = requested_buffer_len + self.remaining_frames_to_record
            if self.num_snapshots_to_sample > 0:
                # Randomly distribute snapshots across the recording
                possible_indices = range(1, total_expected_frames + 1)
                count = min(len(possible_indices), self.num_snapshots_to_sample)
                self.sampled_indices = sorted(random.sample(possible_indices, count))
            else:
                self.sampled_indices = []

            # Write buffer to file
            # If pre_event_seconds was specified, we slice from the end of the buffer
            buffer_to_write = list(self.frame_buffer)
            if pre_event_seconds is not None:
                buffer_to_write = buffer_to_write[-requested_buffer_len:]

            for old_frame_data in buffer_to_write:
                # Unpack tuple
                if isinstance(old_frame_data, tuple):
                    old_frame, old_objects = old_frame_data
                else:
                    # Fallback for legacy buffer items (shouldn't happen on fresh start)
                    old_frame = old_frame_data
                    old_objects = None
                    
                self.current_session_frame += 1
                if self.active_writer:
                    # Write CLEAN frame
                    self.active_writer.write(old_frame)
                
                # Check for snapshots in the pre-buffer
                if self.num_snapshots_to_sample > 0 and self.snapshots_saved_in_session < self.num_snapshots_to_sample:
                    if self.current_session_frame in self.sampled_indices:
                        self.snapshots_saved_in_session += 1
                        snap_dir = os.path.join(self.save_dir, self.active_event_dir) if self.active_event_dir else self.save_dir
                        # Save Annotated Snapshot using stored objects
                        self._save_snapshot(old_frame, "dist", old_objects, custom_dir=snap_dir)

    def _save_snapshot(self, frame, suffix_tag, frame_objects=None, custom_dir=None):
        """Internal helper to save a snapshot."""
        capture_image.capture_frame(
            frame.copy(), # Save a copy to be safe
            self.cam_id, 
            f"{suffix_tag}_{int(time.time())}", 
            self.last_alert_types, 
            custom_dir if custom_dir else self.save_dir, 
            frame_objects=frame_objects
        )

    def _stop_recording(self):
        """Stops the current recording."""
        self.is_recording = False
        if self.active_writer:
            self.active_writer.release()
            self.active_writer = None

        # Signal completion for background uploader
        if self.active_event_dir:
            try:
                event_path = os.path.join(self.save_dir, self.active_event_dir)
                marker_path = os.path.join(event_path, ".upload_ready")
                with open(marker_path, 'w') as f:
                    f.write(str(time.time()))
                # logger.info(f"Marked {self.active_event_dir} as ready for upload")
            except Exception as e:
                logger.error(f"Failed to create upload marker: {e}")