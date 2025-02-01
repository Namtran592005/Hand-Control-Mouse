import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import threading
import keyboard
import sys
import customtkinter as ctk
from tkinter import messagebox

# ================== Cấu hình MediaPipe ==================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ================== Biến toàn cục ==================
screen_w, screen_h = pyautogui.size()
is_running = False
scroll_mode = False
filter = None

# Vô hiệu hóa fail-safe của PyAutoGUI
pyautogui.FAILSAFE = False

# ================== Bộ lọc Kalman ==================
class KalmanFilter:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-4):
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * process_noise
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * measurement_noise
        self.prediction = np.zeros((2, 1), np.float32)

    def update(self, x, y):
        measurement = np.array([[x], [y]], np.float32)
        self.kf.correct(measurement)
        self.prediction = self.kf.predict()
        return self.prediction[0], self.prediction[1]

# ================== Hàm điều khiển chuột ==================
def control_mouse():
    global is_running, scroll_mode, filter
    
    # Khởi động camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Lỗi", "Không thể khởi động camera!")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Độ phân giải cao hơn
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)  # Tăng FPS camera
    
    filter = KalmanFilter()
    
    # Biến để theo dõi trạng thái ngón tay
    prev_index_finger_state = False
    prev_thumb_state = False
    double_click_time = 0
    
    while is_running:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Lỗi", "Không thể đọc hình ảnh từ camera!")
            break
        
        # Lật ảnh camera để điều hướng chính xác
        frame = cv2.flip(frame, 1)
        
        # Xử lý hình ảnh
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = hands.process(rgb_frame)
        
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Lấy tọa độ các ngón tay
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                
                # Tính khoảng cách giữa các ngón tay
                index_thumb_dist = np.linalg.norm(
                    np.array([index_finger_tip.x, index_finger_tip.y]) - 
                    np.array([thumb_tip.x, thumb_tip.y])
                )
                index_middle_dist = np.linalg.norm(
                    np.array([index_finger_tip.x, index_finger_tip.y]) - 
                    np.array([middle_finger_tip.x, middle_finger_tip.y])
                )
                
                # Điều khiển con trỏ bằng đầu ngón trỏ
                x = int(index_finger_tip.x * screen_w)
                y = int(index_finger_tip.y * screen_h)
                
                # Giới hạn tọa độ để tránh fail-safe
                x = max(0, min(x, screen_w - 1))
                y = max(0, min(y, screen_h - 1))
                
                # Làm mịn tọa độ bằng Kalman Filter
                x_smooth, y_smooth = filter.update(x, y)
                pyautogui.moveTo(x_smooth, y_smooth, _pause=False)
                
                # Click chuột trái (ngón trỏ co tròn)
                if index_thumb_dist < 0.05:
                    if not prev_index_finger_state:
                        if (time.time() - double_click_time) < 0.5:
                            pyautogui.doubleClick()  # Double click
                        else:
                            pyautogui.click(button='left')  # Single click
                        double_click_time = time.time()
                    prev_index_finger_state = True
                else:
                    prev_index_finger_state = False
                
                # Click chuột phải (ngón cái co lại)
                if index_thumb_dist < 0.1:
                    if not prev_thumb_state:
                        pyautogui.click(button='right')
                        prev_thumb_state = True
                else:
                    prev_thumb_state = False
                
                # Chế độ cuộn trang (hai ngón trỏ và giữa)
                if index_middle_dist < 0.05:
                    scroll_mode = True
                else:
                    scroll_mode = False
                
                # Cuộn trang lên/xuống
                if scroll_mode:
                    if y < screen_h * 0.4:  # Nhìn lên trên
                        pyautogui.scroll(1)  # Cuộn lên
                    elif y > screen_h * 0.6:  # Nhìn xuống dưới
                        pyautogui.scroll(-1)  # Cuộn xuống
        
        # Hiển thị FPS
        cv2.putText(frame, f"FPS: {int(cap.get(cv2.CAP_PROP_FPS))}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Hand control Mouse", frame)
        
        # Thoát bằng phím ESC
        if cv2.waitKey(1) & 0xFF == 0x1B:
            break
    
    # Giải phóng camera và đóng cửa sổ
    cap.release()
    cv2.destroyAllWindows()

# ================== Hotkey và đa luồng ==================
def stop_program():
    global is_running
    is_running = False
    sys.exit()

# Đăng ký hotkey (Ctrl + Alt + X)
keyboard.add_hotkey('ctrl+alt+x', stop_program)

# ================== Giao diện GUI ==================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Điều khiển bằng tay - Namtran5905")
        self.geometry("400x300")
        
        # Chế độ sáng/tối
        ctk.set_appearance_mode("system")
        
        # Nút bật/tắt
        self.start_btn = ctk.CTkButton(self, text="Bắt đầu", command=self.start)
        self.stop_btn = ctk.CTkButton(self, text="Dừng", command=self.stop)
        self.settings_btn = ctk.CTkButton(self, text="Cài đặt", command=self.open_settings)
        self.info_btn = ctk.CTkButton(self, text="Thông tin", command=self.show_info)
        
        # Bố cục giao diện
        self.start_btn.pack(pady=10)
        self.stop_btn.pack(pady=5)
        self.settings_btn.pack(pady=5)
        self.info_btn.pack(pady=5)
        
    def start(self):
        global is_running
        if is_running:
            messagebox.showinfo("Thông báo", "Chương trình đã chạy!")
            return
        is_running = True
        threading.Thread(target=control_mouse, daemon=True).start()
            
    def stop(self):
        global is_running
        is_running = False
        messagebox.showinfo("Thông báo", "Chương trình đã dừng!")
        
    def open_settings(self):
        messagebox.showinfo("Cài đặt", "Tính năng đang phát triển!")
        
    def show_info(self):
        info = """
        Tên chương trình: Điều khiển bằng tay
        Phiên bản: 1.0
        Nhà phát triển: Namtran5905
        Mô tả: Chương trình điều khiển chuột bằng cử chỉ tay.
        """
        messagebox.showinfo("Thông tin", info)

if __name__ == "__main__":
    app = App()
    app.mainloop()
