import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import numpy as np
import time

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
start_time = time.time()
waiting_mode = False

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

# ================== Hàm điều khiển chuột ==================
def control_mouse():
    global is_running, scroll_mode, start_time, waiting_mode
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    is_running = True
    
    # Biến để theo dõi trạng thái ngón tay
    prev_index_finger_state = False
    prev_thumb_state = False
    double_click_time = 0
    
    while is_running:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Độ trễ 3 giây khi khởi động
        if time.time() - start_time < 3:
            cv2.putText(frame, "Chuẩn bị...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Điều khiển bằng tay", frame)
            cv2.waitKey(1)
            continue
        
        # Xử lý hình ảnh
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = hands.process(rgb_frame)
        
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Vẽ landmarks bàn tay
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Lấy tọa độ đốt đầu tiên của ngón trỏ (đầu ngón trỏ)
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
                
                # Chế độ waiting (bàn tay cung lại ✊)
                if index_thumb_dist < 0.05 and index_middle_dist < 0.05:
                    waiting_mode = True
                    scroll_mode = False
                    cv2.putText(frame, "Chờ...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    continue
                else:
                    waiting_mode = False
                
                # Điều khiển con trỏ bằng đốt đầu tiên của ngón trỏ
                if not scroll_mode and not waiting_mode:
                    x, y = int(index_finger_tip.x * screen_w), int(index_finger_tip.y * screen_h)
                    x_smooth, y_smooth = filter.update(x, y)
                    pyautogui.moveTo(x_smooth, y_smooth, duration=0.1)
                
                # Click chuột trái (ngón trỏ co tròn)
                if index_thumb_dist < 0.05:
                    if not prev_index_finger_state:
                        if (cv2.getTickCount() - double_click_time) / cv2.getTickFrequency() < 0.5:
                            pyautogui.doubleClick()  # Double click
                        else:
                            pyautogui.click(button='left')  # Single click
                        double_click_time = cv2.getTickCount()
                    prev_index_finger_state = True
                else:
                    prev_index_finger_state = False
                
                # Click chuột phải (ngón cái co lại)
                if index_thumb_dist < 0.1 and not prev_thumb_state:
                    pyautogui.click(button='right')
                    prev_thumb_state = True
                elif index_thumb_dist >= 0.1:
                    prev_thumb_state = False
                
                # Chế độ cuộn trang (hai ngón trỏ và giữa)
                if index_middle_dist < 0.05:
                    scroll_mode = True
                else:
                    scroll_mode = False
        
        # Hiển thị HUD
        cv2.putText(frame, f"Che do cuon: {'On' if scroll_mode else 'Off'}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Nhan dien ban tay", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Live View", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    is_running = False

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
        global is_running, start_time
        if not is_running:
            start_time = time.time()
            control_mouse()
            
    def stop(self):
        global is_running
        is_running = False
        
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
