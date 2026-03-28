"""
Debug window for Rubi's vision - shows camera feed with detections
"""

import tkinter as tk
from PIL import Image, ImageTk
import cv2
import time

class VisionDebugWindow:
    """Separate window showing camera feed with detection boxes"""
    
    def __init__(self, camera, root):
        self.camera = camera
        self.root = root  # Use existing Tk root
        self.running = True
        self.last_frame = None
        self.detection_info = []
        
        # Create window as a Toplevel
        self.window = tk.Toplevel(self.root)
        self.window.title("👁️ Rubi Vision Debug")
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Main frame
        main_frame = tk.Frame(self.window, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(main_frame, text="RUBI VISION FEED", 
                        font=('Arial', 16, 'bold'),
                        fg='#00ff00', bg='#2b2b2b')
        title.pack(pady=5)
        
        # Video feed frame
        video_frame = tk.Frame(main_frame, bg='#1a1a1a', relief='sunken', bd=2)
        video_frame.pack(pady=10)
        
        self.video_label = tk.Label(video_frame, bg='#000000')
        self.video_label.pack()
        
        # Detection info panel
        info_frame = tk.Frame(main_frame, bg='#1a1a1a', relief='raised', bd=2)
        info_frame.pack(fill='x', pady=10, padx=10)
        
        # Info header
        tk.Label(info_frame, text="DETECTED OBJECTS", 
                font=('Arial', 12, 'bold'),
                fg='#ffaa00', bg='#1a1a1a').pack(pady=5)
        
        # Scrollable text area for detections
        self.info_text = tk.Text(info_frame, height=8, width=70,
                                 bg='#2b2b2b', fg='#00ff00',
                                 font=('Courier', 10))
        self.info_text.pack(pady=5, padx=10)
        
        # Search status
        self.status_label = tk.Label(info_frame, text="Status: Idle",
                                     font=('Arial', 10),
                                     fg='#888888', bg='#1a1a1a')
        self.status_label.pack(pady=5)
        
        # Start first update
        self._update_display()
        
    def _update_display(self):
        """Update the video feed and detection info"""
        if not self.running:
            return
            
        # Get frame with detections
        frame = self.camera.draw_detections()
        if frame is not None:
            # Convert to RGB and resize for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (640, 480))
            
            # Convert to PhotoImage
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update label
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
            
        # Update detection info
        objects = self.camera.get_current_objects()
        self._update_info(objects)
        
        # Schedule next update
        if self.window:
            self.window.after(50, self._update_display)
            
    def _update_info(self, objects):
        """Update the detection info panel"""
        self.info_text.delete(1.0, tk.END)
        
        if not objects:
            self.info_text.insert(tk.END, "No objects detected\n")
        else:
            for i, obj in enumerate(objects, 1):
                line = (f"{i:2d}. {obj['name']:15s} | "
                       f"Conf: {obj['confidence']:.2f} | "
                       f"Dir: {obj['direction']:6s} | "
                       f"Dist: {obj['distance']:.1f}m\n")
                self.info_text.insert(tk.END, line)
                
    def set_status(self, status):
        """Update the status message"""
        if self.window:
            self.status_label.config(text=f"Status: {status}")
            
    def _on_closing(self):
        """Handle window closing"""
        self.running = False
        if self.window:
            self.window.destroy()