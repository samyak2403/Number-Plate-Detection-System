import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import queue
import time
from plate_detector import NumberPlateDetector
from state_mapper import StateMapper

class NumberPlateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Plate Detection System")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2c3e50')
        
        # Initialize components
        self.detector = NumberPlateDetector()
        self.state_mapper = StateMapper()
        
        # Video processing variables
        self.video_path = None
        self.cap = None
        self.is_playing = False
        self.current_frame = None
        self.detected_plates = []
        
        # Image processing variables
        self.image_path = None
        self.current_image = None
        self.is_image_mode = False
        
        # Threading
        self.frame_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Number Plate Detection System", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Content frame
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Video display
        left_frame = tk.Frame(content_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Video controls
        controls_frame = tk.Frame(left_frame, bg='#34495e')
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.upload_video_btn = tk.Button(controls_frame, text="Upload Video", 
                                   command=self.upload_video, bg='#3498db', fg='white',
                                   font=('Arial', 12, 'bold'), padx=20)
        self.upload_video_btn.pack(side=tk.LEFT, padx=5)

        self.upload_image_btn = tk.Button(controls_frame, text="Upload Image", 
                                   command=self.upload_image, bg='#9b59b6', fg='white',
                                   font=('Arial', 12, 'bold'), padx=20)
        self.upload_image_btn.pack(side=tk.LEFT, padx=5)
        
        self.play_btn = tk.Button(controls_frame, text="Play", 
                                 command=self.toggle_playback, bg='#27ae60', fg='white',
                                 font=('Arial', 12, 'bold'), padx=20, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(controls_frame, text="Stop", 
                                 command=self.stop_video, bg='#e74c3c', fg='white',
                                 font=('Arial', 12, 'bold'), padx=20, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Video display
        self.video_frame = tk.Frame(left_frame, bg='black', height=400)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.video_label = tk.Label(self.video_frame, text="No Video Loaded", 
                                   fg='white', bg='black', font=('Arial', 16))
        self.video_label.pack(expand=True)
        
        # Right side - Information panel
        right_frame = tk.Frame(content_frame, bg='#34495e', relief=tk.RAISED, bd=2, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)
        
        # Info panel title
        info_title = tk.Label(right_frame, text="Detection Information", 
                             font=('Arial', 16, 'bold'), fg='white', bg='#34495e')
        info_title.pack(pady=10)
        
        # Statistics frame
        stats_frame = tk.LabelFrame(right_frame, text="Statistics", fg='white', bg='#34495e',
                                   font=('Arial', 12, 'bold'))
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.plates_detected_label = tk.Label(stats_frame, text="Plates Detected: 0", 
                                             fg='white', bg='#34495e', font=('Arial', 11))
        self.plates_detected_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.accuracy_label = tk.Label(stats_frame, text="Accuracy: 0%", 
                                      fg='white', bg='#34495e', font=('Arial', 11))
        self.accuracy_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Detection results frame
        results_frame = tk.LabelFrame(right_frame, text="Latest Detections", fg='white', bg='#34495e',
                                     font=('Arial', 12, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollable text widget for results
        text_frame = tk.Frame(results_frame, bg='#34495e')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = tk.Text(text_frame, bg='#2c3e50', fg='white', 
                                   font=('Courier', 10), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_label = tk.Label(main_frame, text="Ready", bg='#34495e', fg='white', 
                                    font=('Arial', 10), anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
    def upload_video(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv")]
        )
        
        if file_path:
            self.video_path = file_path
            self.status_label.config(text=f"Video loaded: {file_path.split('/')[-1]}")
            self.play_btn.config(state=tk.NORMAL)
            self.reset_detection_data()
            
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )

        if file_path:
            self.image_path = file_path
            self.status_label.config(text=f"Image loaded: {file_path.split('/')[-1]}")
            self.is_image_mode = True
            self.process_image()
            
    def process_image(self):
        if self.image_path:
            frame = cv2.imread(self.image_path)
            results = self.detector.detect_plates(frame)
            processed_frame = self.draw_detections(frame, results)
            self.update_image_display(processed_frame)
            self.update_detection_info(results)

    def update_image_display(self, frame):
        height, width = frame.shape[:2]
        display_width = 800
        display_height = int(height * (display_width / width))

        resized_frame = cv2.resize(frame, (display_width, display_height))

        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(pil_image)

        self.video_label.config(image=photo, text='')
        self.video_label.image = photo

    def toggle_playback(self):
        if not self.is_playing:
            self.start_video()
        else:
            self.pause_video()
            
    def start_video(self):
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
            self.is_playing = True
            self.play_btn.config(text="Pause", bg='#f39c12')
            self.stop_btn.config(state=tk.NORMAL)
            
            # Start video processing thread
            self.video_thread = threading.Thread(target=self.process_video, daemon=True)
            self.video_thread.start()
            
            # Start UI update thread
            self.update_thread = threading.Thread(target=self.update_ui, daemon=True)
            self.update_thread.start()
            
    def pause_video(self):
        self.is_playing = False
        self.play_btn.config(text="Play", bg='#27ae60')
        
    def stop_video(self):
        self.is_playing = False
        if self.cap:
            self.cap.release()
        self.play_btn.config(text="Play", bg='#27ae60', state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.video_label.config(image='', text="No Video Loaded")
        self.status_label.config(text="Video stopped")
        
    def process_video(self):
        while self.is_playing and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Detect number plates
            results = self.detector.detect_plates(frame)
            
            # Draw bounding boxes and extract text
            processed_frame = self.draw_detections(frame, results)
            
            # Put frame in queue for UI update
            try:
                self.frame_queue.put_nowait((processed_frame, results))
            except queue.Full:
                pass
                
            time.sleep(0.033)  # ~30 FPS
            
    def draw_detections(self, frame, detections):
        processed_frame = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            plate_text = detection.get('text', '')
            
            # Draw green bounding box
            cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw confidence and text
            label = f"{plate_text} ({confidence:.2f})"
            cv2.putText(processed_frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                       
        return processed_frame
        
    def update_ui(self):
        while self.is_playing:
            try:
                frame, detections = self.frame_queue.get_nowait()
                
                # Update video display
                self.update_video_display(frame)
                
                # Update detection information
                self.update_detection_info(detections)
                
            except queue.Empty:
                pass
                
            time.sleep(0.033)
            
    def update_video_display(self, frame):
        # Resize frame to fit display
        height, width = frame.shape[:2]
        display_width = 800
        display_height = int(height * (display_width / width))
        
        resized_frame = cv2.resize(frame, (display_width, display_height))
        
        # Convert to RGB for PIL
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(pil_image)
        
        # Update label
        self.video_label.config(image=photo, text='')
        self.video_label.image = photo
        
    def update_detection_info(self, detections):
        if detections:
            self.detected_plates.extend(detections)
            
            # Update statistics
            total_plates = len(self.detected_plates)
            self.plates_detected_label.config(text=f"Plates Detected: {total_plates}")
            
            # Add new detections to results
            for detection in detections:
                plate_text = detection.get('text', 'Unknown')
                confidence = detection['confidence']
                
                if plate_text and plate_text != 'Unknown':
                    # Extract state code and get location info
                    state_info = self.state_mapper.get_location_info(plate_text)
                    
                    result_text = f"\n{'='*40}\n"
                    result_text += f"Plate: {plate_text}\n"
                    result_text += f"Confidence: {confidence:.2f}%\n"
                    result_text += f"State: {state_info['state']}\n"
                    result_text += f"District: {state_info['district']}\n"
                    result_text += f"Time: {time.strftime('%H:%M:%S')}\n"
                    
                    self.results_text.insert(tk.END, result_text)
                    self.results_text.see(tk.END)
                    
            # Update accuracy (simplified calculation)
            valid_detections = sum(1 for d in detections if d.get('text'))
            if detections:
                accuracy = (valid_detections / len(detections)) * 100
                self.accuracy_label.config(text=f"Accuracy: {accuracy:.1f}%")
                
    def reset_detection_data(self):
        self.detected_plates = []
        self.plates_detected_label.config(text="Plates Detected: 0")
        self.accuracy_label.config(text="Accuracy: 0%")
        self.results_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = NumberPlateApp(root)
    root.mainloop()
