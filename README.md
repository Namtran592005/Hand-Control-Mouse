# Hand Control Mouse
---

### 1. Tổng Quan
Hand Control Mouse là một Chương trình điều khiển máy tính thông minh sử dụng cử chỉ tay thông qua camera. Chương trình cho phép người dùng điều khiển con trỏ chuột và thực hiện các thao tác cơ bản mà không cần chạm vào chuột vật lý.

### 2. Công Nghệ Cốt Lõi

#### 2.1. Xử Lý Hình Ảnh và Nhận Dạng Cử Chỉ
- **MediaPipe Hands**: Framework nhận dạng bàn tay
  - Độ tin cậy phát hiện: 70%
  - Độ tin cậy theo dõi: 70%
  - Chế độ một tay
  - Nhận dạng 21 điểm mốc trên bàn tay

#### 2.2. Xử Lý Tín Hiệu
- **Bộ Lọc Kalman**:
  - Loại bỏ nhiễu và làm mịn chuyển động
  - Process noise: 1e-5
  - Measurement noise: 1e-4
  - Ma trận chuyển đổi 4x4
  - Ma trận đo lường 2x2

#### 2.3. Camera và Video
- Độ phân giải: 1280x720
- Tốc độ khung hình: 60 FPS
- Tự động lật ngang hình ảnh
- Hiển thị FPS thời gian thực
Kém
- Định vị con trỏ: ±5 pixels
- Tỷ lệ nhận diện sai: 80% :)))))

### 7. Phím Tắt và Điều Khiển
- **Ctrl + Alt + X**: Thoát chương trình
- **ESC**: Đóng cửa sổ camera

### 8. Giới Hạn và Lưu Ý
1. Ánh sáng: Cần đủ sáng để nhận diện
2. Nền: Tránh nền phức tạp
3. Khoảng cách: 30-80cm từ camera
4. Góc camera: Thẳng với bàn tay

