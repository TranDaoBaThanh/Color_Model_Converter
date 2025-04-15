# Hướng dẫn thiết lập và chạy ứng dụng Color Model Converter

## Cấu trúc thư mục

```
color-model-converter/
├── app.py                  # File chính của ứng dụng FastAPI
├── shader_manager.py       # Module quản lý shader OpenGL
├── requirements.txt        # Danh sách các thư viện phụ thuộc
├── .env                    # File cấu hình môi trường
└── static/                 # Thư mục chứa các file tĩnh
    ├── index.html          # Giao diện người dùng
    └── script.js           # JavaScript cho UI
```

## Cài đặt

1. **Tạo môi trường ảo Python**:
   ```bash
   python -m venv .venv
   ```

2. **Kích hoạt môi trường ảo**:
   - Trên Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Trên macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Cài đặt các thư viện phụ thuộc**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Lưu ý về OpenGL**: Đảm bảo hệ thống của bạn có hỗ trợ OpenGL. Nếu bạn đang chạy trong môi trường không có GPU (như một số server đám mây), bạn có thể cần cài đặt thêm:
   ```bash
   sudo apt-get install -y xvfb libgl1-mesa-glx
   ```

## Chạy ứng dụng

1. **Khởi động server**:
   ```bash
   python app.py
   ```

2. **Truy cập ứng dụng**: Mở trình duyệt web và truy cập địa chỉ:
   ```
   http://localhost:8000
   ```

## Sử dụng ứng dụng

1. **Tải lên hình ảnh**: Nhấp vào nút "Choose File" để chọn một hình ảnh từ máy tính của bạn.

2. **Chọn mô hình màu**: Từ menu thả xuống, chọn mô hình màu mà bạn muốn chuyển đổi hình ảnh sang.

3. **Điều chỉnh tham số**: Sử dụng các thanh trượt để điều chỉnh các tham số của mô hình màu đã chọn.

4. **Xử lý hình ảnh**: Nhấp vào nút "Upload & Convert" để xử lý hình ảnh ban đầu, hoặc "Apply Changes" để áp dụng các thay đổi tham số mới cho hình ảnh đã tải lên.

5. **Xem kết quả**: Hình ảnh gốc và hình ảnh đã chuyển đổi sẽ được hiển thị bên cạnh nhau để so sánh.

## Xử lý sự cố

- **Lỗi OpenGL**: Nếu bạn gặp lỗi liên quan đến OpenGL, đảm bảo rằng hệ thống của bạn có driver đồ họa phù hợp và hỗ trợ OpenGL 3.3+.

- **Vấn đề tải hình ảnh**: Đảm bảo hình ảnh của bạn là định dạng phổ biến như PNG, JPG, hoặc BMP.

- **Hiệu suất chậm**: Đối với hình ảnh lớn, quá trình xử lý có thể mất nhiều thời gian hơn. Cân nhắc giảm kích thước hình ảnh để cải thiện hiệu suất.