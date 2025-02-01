import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import numpy as np
import speech_recognition as sr

# ================== Cấu hình MediaPipe ==================
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Định nghĩa các điểm landmarks cho mắt (theo MediaPipe)
LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]    # Mắt trái
RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]  # Mắt phải

# ================== Biến toàn cục ==================
screen_w, screen_h = pyautogui.size()
is_running = False
left_eye_closed = False
right_eye_closed = False
scroll_mode = False
text_input_mode = False
recognizer = sr.Recognizer()

# ================== Bộ lọc trung bình động ==================
class MovingAverageFilter:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.x_values = []
        self.y_values = []

    def update(self, x, y):
        self.x_values.append(x)
        self.y_values.append(y)
        
        if len(self.x_values) > self.window_size:
            self.x_values.pop(0)
            self.y_values.pop(0)
        
        return np.mean(self.x_values), np.mean(self.y_values)

# Khởi tạo bộ lọc
filter = MovingAverageFilter(window_size=5)

# ================== Hàm tính tỷ lệ nhắm mắt ==================
def eye_aspect_ratio(eye_landmarks):
    # Tính khoảng cách dọc
    vertical1 = np.linalg.norm(np.array([eye_landmarks[1].x, eye_landmarks[1].y]) - 
                              np.array([eye_landmarks[5].x, eye_landmarks[5].y]))
    vertical2 = np.linalg.norm(np.array([eye_landmarks[2].x, eye_landmarks[2].y]) - 
                              np.array([eye_landmarks[4].x, eye_landmarks[4].y]))
    
    # Tính khoảng cách ngang
    horizontal = np.linalg.norm(np.array([eye_landmarks[0].x, eye_landmarks[0].y]) - 
                               np.array([eye_landmarks[3].x, eye_landmarks[3].y]))
    
    return (vertical1 + vertical2) / (2.0 * horizontal)

# ================== Hàm tính hướng nhìn ==================
def get_gaze_direction(left_eye, right_eye):
    # Tính trung bình vị trí của các điểm landmarks mắt
    left_eye_center = np.mean([(pt.x, pt.y) for pt in left_eye], axis=0)
    right_eye_center = np.mean([(pt.x, pt.y) for pt in right_eye], axis=0)
    
    # Tính vector hướng nhìn
    gaze_vector = (right_eye_center + left_eye_center) / 2
    return gaze_vector

# ================== Hàm nhận diện giọng nói ==================
def recognize_speech():
    with sr.Microphone() as source:
        print("Đang nghe...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language="vi-VN")
            print("Bạn nói:", text)
            pyautogui.write(text)  # Nhập văn bản vào ứng dụng hiện tại
        except sr.UnknownValueError:
            print("Không nhận diện được giọng nói")
        except sr.RequestError:
            print("Lỗi kết nối đến dịch vụ nhận diện giọng nói")

# ================== Hàm điều khiển chuột ==================
def control_mouse():
    global is_running, left_eye_closed, right_eye_closed, scroll_mode, text_input_mode
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    is_running = True
    
    # Lịch sử tỷ lệ nhắm mắt
    left_ear_history = []
    right_ear_history = []
    
    while is_running:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Xử lý hình ảnh
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_results = face_mesh.process(rgb_frame)
        hand_results = hands.process(rgb_frame)
        
        # Nhận diện bàn tay
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Vẽ landmarks bàn tay
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Kích hoạt chế độ cuộn trang hoặc nhập văn bản
                if hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x > 0.7:
                    scroll_mode = True
                    text_input_mode = False
                elif hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x < 0.3:
                    scroll_mode = False
                    text_input_mode = True
                    recognize_speech()
                else:
                    scroll_mode = False
                    text_input_mode = False
        
        # Nhận diện khuôn mặt và mắt
        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            
            # Lấy landmarks mắt
            left_eye = [face_landmarks.landmark[i] for i in LEFT_EYE_INDICES]
            right_eye = [face_landmarks.landmark[i] for i in RIGHT_EYE_INDICES]
            
            # Tính hướng nhìn
            gaze_vector = get_gaze_direction(left_eye, right_eye)
            x, y = int(gaze_vector[0] * screen_w), int(gaze_vector[1] * screen_h)
            
            # Làm mịn tọa độ
            x_smooth, y_smooth = filter.update(x, y)
            
            # Điều khiển con trỏ hoặc cuộn trang
            if scroll_mode:
                if y < screen_h * 0.4:  # Nhìn lên trên
                    pyautogui.scroll(1)  # Cuộn lên
                elif y > screen_h * 0.6:  # Nhìn xuống dưới
                    pyautogui.scroll(-1)  # Cuộn xuống
            else:
                pyautogui.moveTo(x_smooth, y_smooth, duration=0.1)
            
            # Tính tỷ lệ nhắm mắt
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            
            # Cập nhật ngưỡng động
            left_threshold = np.mean(left_ear_history) if left_ear_history else left_ear
            right_threshold = np.mean(right_ear_history) if right_ear_history else right_ear
            
            left_ear_history.append(left_ear)
            right_ear_history.append(right_ear)
            
            if len(left_ear_history) > 10:
                left_ear_history.pop(0)
                right_ear_history.pop(0)
            
            # Phát hiện nháy mắt
            if left_ear < left_threshold * 0.8:
                if not left_eye_closed:
                    pyautogui.click(button='left')
                    left_eye_closed = True
            else:
                left_eye_closed = False
                
            if right_ear < right_threshold * 0.8:
                if not right_eye_closed:
                    pyautogui.click(button='right')
                    right_eye_closed = True
            else:
                right_eye_closed = False
        
        # Hiển thị HUD
        cv2.putText(frame, f"Scroll Mode: {scroll_mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Text Input Mode: {text_input_mode}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Eye Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    is_running = False

# ================== Giao diện GUI ==================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Eye Control Mouse")
        self.geometry("400x300")
        
        # Chế độ sáng/tối
        ctk.set_appearance_mode("system")
        
        # Nút bật/tắt
        self.start_btn = ctk.CTkButton(self, text="Start", command=self.start)
        self.stop_btn = ctk.CTkButton(self, text="Stop", command=self.stop)
        
        # Bố cục giao diện
        self.start_btn.pack(pady=10)
        self.stop_btn.pack(pady=5)
        
    def start(self):
        if not is_running:
            control_mouse()
            
    def stop(self):
        global is_running
        is_running = False

if __name__ == "__main__":
    app = App()
    app.mainloop()
