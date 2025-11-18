import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import queue
import time
from tkinter import Tk, Label, Button, messagebox, Frame, StringVar
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque


# -------------------- Voice System --------------------
speech_queue = queue.Queue()
voice_enabled = True

def voice_worker():
    """Background thread for sequential speech output."""
    while True:
        text = speech_queue.get()
        if text is None:
            break
        if not voice_enabled:
            speech_queue.task_done()
            continue
        try:
            e = pyttsx3.init()
            e.setProperty('rate', 150)
            e.setProperty('volume', 0.9)
            voices = e.getProperty('voices')
            if len(voices) > 1:
                e.setProperty('voice', voices[1].id)
            e.say(text)
            e.runAndWait()
            e.stop()
            del e
        except Exception as ex:
            print("Voice error:", ex)
        speech_queue.task_done()

threading.Thread(target=voice_worker, daemon=True).start()

def speak(text):
    if voice_enabled:
        speech_queue.put(text)


# -------------------- AI Setup --------------------
mp_face = mp.solutions.face_detection
face_detection = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6)


# -------------------- GUI App --------------------
class AICameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Camera Guidance")
        self.running = False

        # Camera and control variables
        self.cap = None
        self.center_count = 0
        self.stable_frames = 7
        self.tolerance = 70
        self.last_speech_time = 0
        self.speech_delay = 1.5
        self.lighting_warning = False
        self.last_light_check = 0
        self.light_check_delay = 3
        self.tracking_enabled = True
        self.last_direction = ""
        self.snapshot_counter = 1
        self.prev_time = 0
        self.fps = 0

        # ---- Performance Metrics ----
        self.total_frames = 0
        self.detected_frames = 0
        self.avg_latency = 0
        self.last_command_time = 0
        self.response_efficiency = 0

        # ---- Data Buffers for Graphs ----
        self.fps_data = deque(maxlen=50)
        self.accuracy_data = deque(maxlen=50)
        self.latency_data = deque(maxlen=50)
        self.response_data = deque(maxlen=50)

        # -------------------- GUI Layout --------------------
        self.video_label = Label(root, bg="black")
        self.video_label.pack(fill="both", expand=True)

        # Metrics Text
        metrics_frame = Frame(root, bg="#1c1c1c")
        metrics_frame.pack(fill="x", pady=(0, 5))
        self.metrics_var = StringVar()
        self.metrics_label = Label(metrics_frame, textvariable=self.metrics_var, fg="cyan",
                                   bg="#1c1c1c", font=("Consolas", 10))
        self.metrics_label.pack(anchor="w", padx=10)

        # Matplotlib Graphs
        self.fig, self.axs = plt.subplots(2, 2, figsize=(6, 3))
        plt.tight_layout(pad=1.5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=False)

        # Initialize subplots
        titles = ["FPS", "Tracking Accuracy (%)", "Latency (ms)", "Response Efficiency (ms)"]
        self.lines = []
        for ax, title in zip(self.axs.flat, titles):
            ax.set_title(title, color="white", fontsize=8)
            ax.set_facecolor("#1c1c1c")
            ax.tick_params(colors="white", labelsize=7)
            line, = ax.plot([], [], color="cyan")
            self.lines.append(line)
        self.fig.patch.set_facecolor("#111")

        # Status Bar
        self.status_var = StringVar(value="Idle")
        self.status_bar = Label(root, textvariable=self.status_var, font=("Helvetica", 11),
                                bg="#333", fg="white", anchor="w", padx=10)
        self.status_bar.pack(fill="x", side="bottom")

        # Control Panel
        control_frame = Frame(root, bg="#222")
        control_frame.pack(fill="x", pady=5)

        self.start_btn = Button(control_frame, text="▶ Start", width=10, command=self.start_camera,
                                bg="#28a745", fg="white", font=("Helvetica", 10, "bold"))
        self.start_btn.pack(side="left", padx=5, pady=5)

        self.stop_btn = Button(control_frame, text="⏹ Stop", width=10, command=self.stop_camera,
                               bg="#dc3545", fg="white", font=("Helvetica", 10, "bold"), state="disabled")
        self.stop_btn.pack(side="left", padx=5, pady=5)

        self.voice_btn = Button(control_frame, text="🔊 Voice: ON", width=12, bg="#007bff", fg="white",
                                font=("Helvetica", 10, "bold"), command=self.toggle_voice)
        self.voice_btn.pack(side="left", padx=5, pady=5)

        self.snapshot_btn = Button(control_frame, text="📸 Snapshot", width=12, bg="#ffc107", fg="black",
                                   font=("Helvetica", 10, "bold"), command=self.take_snapshot)
        self.snapshot_btn.pack(side="left", padx=5, pady=5)

        self.exit_btn = Button(control_frame, text="❌ Exit", width=10, bg="#6c757d", fg="white",
                               font=("Helvetica", 10, "bold"), command=self.on_exit)
        self.exit_btn.pack(side="right", padx=5, pady=5)

        # Status color indicator
        self.color_indicator = Label(root, height=2, bg="#555")
        self.color_indicator.pack(fill="x")

        # Graph Update
        self.root.after(1000, self.update_graphs)

    # -------------------- Camera Controls --------------------
    def start_camera(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Unable to access camera.")
            return
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_var.set("Running...")
        self.update_frame()

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Stopped")
        self.video_label.config(image='')
        self.color_indicator.config(bg="#555")

    def toggle_voice(self):
        global voice_enabled
        voice_enabled = not voice_enabled
        self.voice_btn.config(
            text="🔇 Voice: OFF" if not voice_enabled else "🔊 Voice: ON",
            bg="#6c757d" if not voice_enabled else "#007bff"
        )

    def take_snapshot(self):
        if not self.cap or not self.running:
            messagebox.showinfo("Info", "Start the camera first!")
            return
        ret, frame = self.cap.read()
        if ret:
            filename = f"snapshot_{self.snapshot_counter}.jpg"
            cv2.imwrite(filename, frame)
            self.snapshot_counter += 1
            messagebox.showinfo("Snapshot Saved", f"✅ Image saved as {filename}")

    # -------------------- Frame Update --------------------
    def update_frame(self):
        if not self.running or not self.cap:
            return

        frame_start_time = time.time()
        success, frame = self.cap.read()
        if not success:
            self.root.after(10, self.update_frame)
            return

        self.total_frames += 1
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb)
        hand_results = hands.process(rgb)

        cx_ref, cy_ref = w // 2, h // 2
        cv2.circle(frame, (cx_ref, cy_ref), 5, (0, 255, 255), -1)
        cv2.rectangle(frame, (cx_ref - self.tolerance, cy_ref - self.tolerance),
                      (cx_ref + self.tolerance, cy_ref + self.tolerance), (255, 255, 0), 2)

        dir_text = "No Face Detected"

        # -------------------- Gesture Controls --------------------
        if hand_results.multi_hand_landmarks:
            hand_landmarks = hand_results.multi_hand_landmarks[0]
            finger_tips = [4, 8, 12, 16, 20]
            h_count = sum(1 for tip in finger_tips
                          if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y)

            if h_count >= 4:
                if self.tracking_enabled:
                    self.tracking_enabled = False
                    speak("Tracking paused")
            elif h_count <= 1:
                if not self.tracking_enabled:
                    self.tracking_enabled = True
                    speak("Tracking resumed")

        # -------------------- Face Tracking --------------------
        if self.tracking_enabled and results.detections:
            self.detected_frames += 1
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x, y, bw, bh = int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)
                cx, cy = x + bw // 2, y + bh // 2

                cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (255, 0, 0), -1)

                dx, dy = cx - cx_ref, cy - cy_ref
                dir_text = ""

                if abs(dx) > self.tolerance:
                    dir_text += "Move Left" if dx > 0 else "Move Right"
                    self.center_count = 0
                if abs(dy) > self.tolerance:
                    dir_text += " Move Down" if dy > 0 else " Move Up"
                    self.center_count = 0

                if abs(dx) <= self.tolerance and abs(dy) <= self.tolerance:
                    self.center_count += 1
                    if self.center_count >= self.stable_frames:
                        dir_text = "Centered [OK]"
                else:
                    self.center_count = 0

        # -------------------- Lighting Feedback --------------------
        now = time.time()
        if now - self.last_light_check > self.light_check_delay:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            if brightness < 60:
                if not self.lighting_warning:
                    self.lighting_warning = True
                    speak("Lighting too low. Please increase brightness.")
            else:
                if self.lighting_warning:
                    self.lighting_warning = False
                    speak("Lighting is okay.")
            self.last_light_check = now

        if self.lighting_warning:
            cv2.putText(frame, "⚠️ Lighting Too Low", (30, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # -------------------- Voice Directions --------------------
        if dir_text != "No Face Detected" and dir_text != self.last_direction:
            if time.time() - self.last_speech_time > self.speech_delay:
                speak(dir_text)
                self.last_direction = dir_text
                self.response_efficiency = (time.time() - frame_start_time) * 1000
                self.last_speech_time = time.time()

        # -------------------- FPS & Latency --------------------
        current_time = time.time()
        if self.prev_time > 0:
            self.fps = 1 / (current_time - self.prev_time)
        self.prev_time = current_time

        frame_latency = (current_time - frame_start_time) * 1000
        self.avg_latency = 0.9 * self.avg_latency + 0.1 * frame_latency

        # -------------------- Metrics Display --------------------
        tracking_accuracy = (self.detected_frames / self.total_frames * 100) if self.total_frames else 0
        self.metrics_var.set(
            f"Tracking Accuracy: {tracking_accuracy:.1f}%   FPS: {int(self.fps)}   Latency: {self.avg_latency:.1f} ms   Response Efficiency: {self.response_efficiency:.1f} ms"
        )

        # Add to graph data
        self.fps_data.append(self.fps)
        self.accuracy_data.append(tracking_accuracy)
        self.latency_data.append(self.avg_latency)
        self.response_data.append(self.response_efficiency)

        # -------------------- Color Indicator --------------------
        if not self.tracking_enabled:
            self.color_indicator.config(bg="#ff3333")
        elif dir_text == "Centered [OK]":
            self.color_indicator.config(bg="#28a745")
        elif dir_text == "No Face Detected":
            self.color_indicator.config(bg="#555")
        else:
            self.color_indicator.config(bg="#ffc107")

        # -------------------- Display --------------------
        cv2.putText(frame, dir_text, (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(Image.fromarray(img_rgb))
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

        self.root.after(30, self.update_frame)

    # -------------------- Graph Update --------------------
    def update_graphs(self):
        metrics = [
            self.fps_data, self.accuracy_data,
            self.latency_data, self.response_data
        ]
        for line, data in zip(self.lines, metrics):
            line.set_data(range(len(data)), list(data))
            ax = line.axes
            ax.relim()
            ax.autoscale_view()
        self.canvas.draw_idle()
        self.root.after(1000, self.update_graphs)

    def on_exit(self):
        self.stop_camera()
        speech_queue.put(None)
        self.root.destroy()


# -------------------- Run App --------------------
if __name__ == "__main__":
    root = Tk()
    app = AICameraApp(root)
    root.geometry("900x820")
    root.configure(bg="#111")
    root.mainloop()
