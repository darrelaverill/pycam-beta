import cv2
import numpy as np
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from datetime import datetime
import os
from kivy.core.window import Window

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.height = self.width
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0.5, 0.8, 1)
            Ellipse(pos=self.pos, size=(self.width, self.height))

class SquareButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.5, 0.8, 0.5, 1)
            Rectangle(pos=self.pos, size=self.size)

class CameraApp(App):
    def build(self):
        self.layout = FloatLayout()
        self.img = Image()
        self.layout.add_widget(self.img)

        self.initial_orientation = None
        self.current_orientation = None

        # Mode switch
        self.mode_switch = Switch(active=False, size_hint=(None, None), size=(100, 50), pos=(10, 140))
        self.mode_switch.bind(active=self.switch_mode)
        self.layout.add_widget(self.mode_switch)
        self.mode_label = Label(text="Photo Mode", size_hint=(None, None), size=(100, 30), pos=(120, 150))
        self.layout.add_widget(self.mode_label)

        # Capture/Record button
        self.action_btn = RoundedButton(text='Capture', size_hint=(None, None), size=(80, 80),
                                        pos_hint={'center_x': 0.5, 'y': 0.05})
        self.action_btn.bind(on_press=self.on_action)
        self.layout.add_widget(self.action_btn)

        # Stabilization button
        self.stab_btn = SquareButton(text='Stabilize: OFF', size_hint=(None, None), size=(120, 50),
                                      pos_hint={'right': 0.98, 'top': 0.98})
        self.stab_btn.bind(on_press=self.toggle_stabilization)
        self.layout.add_widget(self.stab_btn)

        # Zoom slider
        self.zoom_slider = Slider(min=0.5, max=5, value=1, orientation='vertical',
                                  size_hint=(None, None), size=(50, 300),
                                  pos_hint={'right': 0.98, 'center_y': 0.5})
        self.zoom_slider.bind(value=self.on_zoom)
        self.layout.add_widget(self.zoom_slider)

        self.ultrawide_effect = 0
        self.capture = cv2.VideoCapture(0)  # Ganti dengan URL kamera jika perlu
        self.is_recording = False
        self.video_mode = False
        self.stabilization_on = False
        self.video_writer = None
        self.prev_frame = None
        Clock.schedule_interval(self.update, 1.0 / 30.0)

        return self.layout

    def detect_orientation(self, frame):
        h, w = frame.shape[:2]
        return 'landscape' if w > h else 'portrait'

    def rotate_frame(self, frame, orientation):
        if orientation == 'portrait':
            return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        return frame

    def switch_mode(self, instance, value):
        self.video_mode = value
        if value:
            self.mode_label.text = "Video Mode"
            self.action_btn.text = "Record"
        else:
            self.mode_label.text = "Photo Mode"
            self.action_btn.text = "Capture"
            if self.is_recording:
                self.stop_recording()

    def toggle_stabilization(self, instance):
        self.stabilization_on = not self.stabilization_on
        self.stab_btn.text = f"Stabilize: {'ON' if self.stabilization_on else 'OFF'}"

    def apply_ultrawide_effect(self, frame, intensity):
        h, w = frame.shape[:2]
        dist_coeff = np.zeros((4, 1), np.float64)
        k1, k2 = -0.2 * intensity, 0.1 * intensity
        p1, p2 = 0.0, 0.0
        dist_coeff[0, 0] = k1
        dist_coeff[1, 0] = k2
        dist_coeff[2, 0] = p1
        dist_coeff[3, 0] = p2

        cam_matrix = np.array([[w, 0, w / 2], [0, h, h / 2], [0, 0, 1]], dtype="double")
        new_cam_matrix, roi = cv2.getOptimalNewCameraMatrix(cam_matrix, dist_coeff, (w, h), 1, (w, h))

        undistorted = cv2.undistort(frame, cam_matrix, dist_coeff, None, new_cam_matrix)

        x, y, w, h = roi
        undistorted = undistorted[y:y + h, x:x + w]
        undistorted = cv2.resize(undistorted, (frame.shape[1], frame.shape[0]))

        return undistorted

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Detect current orientation
            self.current_orientation = self.detect_orientation(frame)

            if self.video_mode:
                if self.is_recording:
                    if self.initial_orientation is None:
                        self.initial_orientation = self.current_orientation
                    frame = self.rotate_frame(frame, self.initial_orientation)
                else:
                    frame = self.rotate_frame(frame, self.current_orientation)
            else:  # Photo mode
                frame = self.rotate_frame(frame, self.current_orientation)

            zoom = self.zoom_slider.value

            # Calculate intensity for ultra-wide effect
            if zoom < 1:
                self.ultrawide_effect = (1 - zoom) * 2
            else:
                self.ultrawide_effect = 0

            # Apply ultra-wide effect if zoom < 1
            if zoom < 1:
                frame = self.apply_ultrawide_effect(frame, self.ultrawide_effect)

            # Apply zoom if zoom > 1
            if zoom > 1:
                h, w = frame.shape[:2]
                center_x, center_y = int(w / 2), int(h / 2)
                radius_x, radius_y = int(w / (2 * zoom)), int(h / (2 * zoom))

                min_x, max_x = center_x - radius_x, center_x + radius_x
                min_y, max_y = center_y - radius_y, center_y + radius_y

                frame = frame[min_y:max_y, min_x:max_x]
                frame = cv2.resize(frame, (w, h))

            if self.video_mode and self.stabilization_on:
                if self.prev_frame is not None:
                    prev_gray = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY)
                    curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None,
                                                        pyr_scale=0.5,
                                                        levels=3,
                                                        winsize=15,
                                                        iterations=3,
                                                        poly_n=5,
                                                        poly_sigma=1.2,
                                                        flags=0)

                    dx = np.mean(flow[:, :, 0])
                    dy = np.mean(flow[:, :, 1])

                    M = np.float32([[1, 0, dx], [0, 1, dy]])
                    frame = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))

            self.prev_frame = frame

            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)

            buf = cv2.flip(frame, 0).tobytes()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            # Update Image widget
            self.img.texture = image_texture

    def on_action(self, instance):
        if self.video_mode:
            if not self.is_recording:
                self.start_recording()
            else:
                self.stop_recording()
        else:
            self.capture_photo()

    def start_recording(self):
        self.is_recording = True
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"/sdcard/Movies/video_{timestamp}.mp4"  # Ganti dengan path yang sesuai
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 30
        self.video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (int(self.capture.get(3)), int(self.capture.get(4))))
        print(f"Recording started: {video_filename}")

    def stop_recording(self):
        self.is_recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            print("Recording stopped.")

    def capture_photo(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"/sdcard/Pictures/photo_{timestamp}.jpg"  # Ganti dengan path yang sesuai
        ret, frame = self.capture.read()
        if ret:
            cv2.imwrite(image_filename, frame)
            print(f"Photo saved: {image_filename}")
    def on_zoom(self, instance, value):
        print(f"Zoom level changed to {value}")
    

if __name__ == '__main__':
    CameraApp().run()
