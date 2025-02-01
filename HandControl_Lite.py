import threading
import time
import cv2
import numpy as np
import tensorflow as tf
import tkinter as tk
from tkinter import ttk

# --- Cấu hình camera ---
DESIRED_WIDTH = 1280
DESIRED_HEIGHT = 720

# --- Giao diện tiến trình (Progress Window) ---
class ProgressWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Khởi tạo chương trình")
        self.geometry("400x120")
        self.resizable(False, False)
        self.label = tk.Label(self, text="Đang khởi tạo...")
        self.label.pack(pady=10)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

    def set_progress(self, value):
        self.progress["value"] = value
        self.label.config(text=f"Tiến trình: {value}%")
        self.update_idletasks()

# --- Hàm khởi tạo camera ---
def initialize_camera(update_progress_callback):
    # Mở camera mặc định (ID=0)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, DESIRED_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DESIRED_HEIGHT)
    # Cập nhật tiến trình: 30%
    update_progress_callback(30)
    time.sleep(0.5)  # Giả lập thời gian khởi tạo
    return cap

# --- Hàm load và tối ưu mô hình ---
def load_and_optimize_model(update_progress_callback):
    model = None
    try:
        # Load mô hình đã huấn luyện
        model = tf.keras.models.load_model("hand_gesture_model.h5")
        print("Load mô hình thành công!")
    except Exception as e:
        print("Không thể load mô hình. Chạy chế độ mô phỏng. Chi tiết:", e)
    
    # Giả lập thời gian load mô hình
    time.sleep(0.5)
    update_progress_callback(60)
    return model

# --- Tiền xử lý frame cho mô hình ---
def preprocess_frame(frame):
    # Giả sử mô hình cần kích thước 224x224
    INPUT_WIDTH = 224
    INPUT_HEIGHT = 224
    processed = cv2.resize(frame, (INPUT_WIDTH, INPUT_HEIGHT))
    processed = processed.astype("float32") / 255.0  # Chuẩn hóa về [0,1]
    return processed

# --- Hàm chạy inference trên frame ---
def run_inference(model, frame):
    # Nếu model chưa được load, chạy chế độ mô phỏng (random)
    if model is None:
        gesture = np.random.choice(["Click trái", "Click phải", "Cuộn", "Chờ", "None"])
        return gesture
    else:
        processed = preprocess_frame(frame)
        input_data = np.expand_dims(processed, axis=0)
        predictions = model.predict(input_data)
        # Giả sử mô hình trả về xác suất cho 4 cử chỉ
        gesture_index = np.argmax(predictions)
        gesture_names = ["Click trái", "Click phải", "Cuộn", "Chờ"]
        if gesture_index < len(gesture_names):
            return gesture_names[gesture_index]
        else:
            return "Unknown"

# --- Hàm live view (vòng lặp xử lý video và nhận diện) ---
def live_view_loop(cap, model):
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Chạy nhận diện cử chỉ trên frame
        gesture = run_inference(model, frame)
        # Hiển thị kết quả nhận diện lên frame
        cv2.putText(frame, f"Gesture: {gesture}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("Live View", frame)

        # Nhấn 'q' để thoát live view
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# --- Hàm khởi chạy live view ---
def start_live_view(cap, model, update_progress_callback):
    update_progress_callback(90)
    # Chạy live view trong một luồng riêng biệt
    live_thread = threading.Thread(target=live_view_loop, args=(cap, model))
    live_thread.daemon = True  # Cho phép thoát khi main thread kết thúc
    live_thread.start()
    update_progress_callback(100)

# --- Hàm main khởi tạo toàn bộ chương trình ---
def main():
    # Tạo cửa sổ tiến trình
    progress_win = ProgressWindow()

    # Hàm cập nhật tiến trình
    def update_progress(value):
        progress_win.set_progress(value)

    # Hàm khởi tạo các thành phần trên luồng riêng để không chặn giao diện Tkinter
    def initialization():
        cap = initialize_camera(update_progress)
        model = load_and_optimize_model(update_progress)
        start_live_view(cap, model, update_progress)
        time.sleep(0.5)  # Đợi vài giây trước khi đóng cửa sổ progress
        progress_win.destroy()  # Đóng cửa sổ tiến trình khi hoàn tất

    # Khởi chạy quá trình khởi tạo trên một luồng riêng
    init_thread = threading.Thread(target=initialization)
    init_thread.daemon = True
    init_thread.start()

    # Chạy vòng lặp giao diện của Tkinter
    progress_win.mainloop()

if __name__ == "__main__":
    main()
