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

### 3. Tính Năng Chi Tiết

#### 3.1. Điều Khiển Con Trỏ
- Di chuyển con trỏ theo đầu ngón trỏ
- Tọa độ được giới hạn trong màn hình
- Chuyển động mượt mà nhờ bộ lọc Kalman

#### 3.2. Thao Tác Chuột
1. **Click Trái**:
   - Chạm ngón trỏ và ngón cái
   - Khoảng cách kích hoạt: < 0.05
   - Hỗ trợ double-click tự động (0.5s)

2. **Click Phải**:
   - Co ngón cái
   - Khoảng cách kích hoạt: < 0.1

3. **Cuộn Trang**:
   - Chạm ngón trỏ và ngón giữa
   - Khoảng cách kích hoạt: < 0.05
   - Vùng cuộn lên: trên 40% màn hình
   - Vùng cuộn xuống: dưới 60% màn hình

### 4. Giao Diện Người Dùng

#### 4.1. Cửa Sổ Chính
- Thiết kế tối giản với CustomTkinter
- Tự động theo chế độ sáng/tối của hệ thống
- Kích thước: 400x300 pixels

#### 4.2. Các Nút Chức Năng
1. **Bắt đầu**: Khởi động nhận dạng
2. **Dừng**: Tạm dừng hệ thống
3. **Cài đặt**: Tùy chỉnh (đang phát triển)
4. **Thông tin**: Hiển thị thông tin phiên bản

### 5. Yêu Cầu Hệ Thống

#### 5.1. Phần Cứng Tối Thiểu
- CPU: Intel Core i5 gen 8 hoặc tương đương
- RAM: 8GB
- Camera: 30 FPS, độ phân giải 720p
- GPU: NVIDIA GTX 1050 hoặc tương đương

#### 5.2. Phần Cứng Đề Xuất
- CPU: Intel Core i7 gen 10 trở lên
- RAM: 16GB
- Camera: 60 FPS, độ phân giải 1080p
- GPU: NVIDIA GTX 1660 hoặc tốt hơn

#### 5.3. Phần Mềm
- Windows 10/11 64-bit
- Python 3.8 trở lên
- Các thư viện:
  - OpenCV
  - MediaPipe
  - PyAutoGUI
  - NumPy
  - CustomTkinter
  - Keyboard

### 6. Hiệu Năng và Độ Chính Xác

#### 6.1. Độ Trễ
- Trễ camera: ~16.7ms (60 FPS)
- Trễ xử lý: ~5-10ms
- Trễ tổng: ~25ms

#### 6.2. Độ Chính Xác
- Nhận dạng cử chỉ: 
- Định vị con trỏ: ±5 pixels
- Tỷ lệ nhận diện sai: 

### 7. Phím Tắt và Điều Khiển
- **Ctrl + Alt + X**: Thoát chương trình
- **ESC**: Đóng cửa sổ camera

### 8. Giới Hạn và Lưu Ý
1. Ánh sáng: Cần đủ sáng để nhận diện
2. Nền: Tránh nền phức tạp
3. Khoảng cách: 30-80cm từ camera
4. Góc camera: Thẳng với bàn tay

