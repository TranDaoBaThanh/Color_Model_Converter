# 🎨 Color Model Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0+-green.svg)](https://fastapi.tiangolo.com/)

**Color Model Converter** là ứng dụng web cho phép chuyển đổi hình ảnh giữa các mô hình màu phổ biến một cách trực quan và hiệu quả. Dự án này sử dụng FastAPI làm backend và OpenGL Shaders để xử lý chuyển đổi màu sắc hiệu suất cao.

## 📚 Giới thiệu về mô hình màu

Mô hình màu (Color Model) là phương pháp toán học để biểu diễn màu sắc bằng các giá trị số. Trong đồ họa máy tính, có rất nhiều mô hình màu khác nhau, nhưng dự án này tập trung vào các mô hình màu phổ biến và thông dụng nhất trong đồ họa máy tính và xử lý hình ảnh.

### Tổng quan về các mô hình màu phổ biến

Trong vô số mô hình màu hiện có, một số mô hình màu được sử dụng rộng rãi hơn trong các ứng dụng thực tế như thiết kế đồ họa, nhiếp ảnh kỹ thuật số, phát triển web, video và in ấn. Dự án Color Model Converter này triển khai các mô hình màu phổ biến nhất, bao gồm:

#### 1. Mô hình màu cộng (Additive)

Mô hình màu cộng tạo ra màu sắc bằng cách kết hợp ánh sáng:

- **RGB (Red, Green, Blue)**: Nền tảng của hầu hết hiển thị kỹ thuật số, mỗi pixel được biểu diễn bởi ba giá trị đỏ, xanh lá, xanh dương.
- **sRGB**: Tiêu chuẩn RGB được sử dụng phổ biến trên web và đa số màn hình.
- **Adobe RGB**: Không gian màu rộng hơn sRGB, phổ biến trong nhiếp ảnh chuyên nghiệp.

#### 2. Mô hình màu trừ (Subtractive)

- **CMYK (Cyan, Magenta, Yellow, Key/Black)**: Tiêu chuẩn trong ngành công nghiệp in ấn, sử dụng bốn màu mực để tạo ra các màu khác nhau trên giấy.

#### 3. Mô hình màu theo cảm nhận (Perceptual)

Các mô hình biểu diễn màu sắc theo cách tương tự với cách con người cảm nhận màu:

- **HSV (Hue, Saturation, Value)**: Trực quan và dễ sử dụng cho việc chọn màu.
- **HSL (Hue, Saturation, Lightness)**: Tương tự HSV nhưng với cách tiếp cận khác về độ sáng.

#### 4. Mô hình màu chuyên dụng

- **YCbCr (Luminance, Chroma Blue, Chroma Red)**: Phổ biến trong xử lý video và nén hình ảnh như JPEG.
- **Grayscale**: Biểu diễn hình ảnh chỉ với các mức độ sáng khác nhau, không có thông tin màu sắc.

Dự án này tập trung vào các mô hình màu phổ biến nhất để đảm bảo tính thực tiễn và ứng dụng cao, thay vì cố gắng triển khai toàn bộ các mô hình màu hiện có trong lý thuyết màu sắc.

## ✨ Tính năng

- 🖼️ Tải lên và xử lý hình ảnh từ máy tính
- 🔄 Chuyển đổi giữa các mô hình màu phổ biến
- 🎚️ Điều chỉnh tham số màu sắc theo thời gian thực
- 📊 Hiển thị hình ảnh gốc và đã xử lý để so sánh
- ⚡ Xử lý hiệu suất cao nhờ GPU thông qua OpenGL Shaders

## 🔧 Cấu trúc thư mục

```
color-model-converter/
├── main.py                  # File chính của ứng dụng FastAPI, chứa logic backend và chạy server
├── shader_manager.py       # Module quản lý shader OpenGL để xử lý chuyển đổi mô hình màu
├── requirements.txt        # Danh sách các thư viện phụ thuộc cần cài đặt
├── .env                    # File cấu hình môi trường, định nghĩa biến như PORT (mặc định: 8000)
└── static/                 # Thư mục chứa các file tĩnh cho giao diện người dùng
    ├── index.html          # Giao diện người dùng (HTML) cho ứng dụng web
    ├── script.js           # JavaScript xử lý tương tác UI và gửi yêu cầu đến backend
    └── style.css           # CSS định dạng giao diện người dùng
```

## 📋 Yêu cầu hệ thống

- Python 3.7 trở lên
- Các thư viện được liệt kê trong file `requirements.txt`
- Trình duyệt web hiện đại hỗ trợ JavaScript và WebGL

## 🚀 Hướng dẫn cài đặt

### 1. Clone repository

```bash
git clone https://github.com/yourusername/color-model-converter.git
cd color-model-converter
```

### 2. Tạo và kích hoạt môi trường ảo Python

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Cài đặt các thư viện phụ thuộc

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường (tuỳ chọn)

Tạo file `.env` để cấu hình các biến môi trường:

```
PORT=8000
```

## 🖥️ Chạy ứng dụng

### Khởi động server

```bash
python app.py
```

Sau khi khởi động thành công, bạn sẽ thấy thông báo tương tự như sau:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

### Truy cập ứng dụng

Mở trình duyệt web và truy cập địa chỉ:
```
http://localhost:8000
```

## 📝 Hướng dẫn sử dụng

### 1. Tải lên hình ảnh
- Nhấp vào nút **"Choose Image"** để chọn một hình ảnh từ máy tính.
- Hình ảnh sẽ được hiển thị ở phần "Original Image".

### 2. Chọn mô hình màu
- Từ menu thả xuống, chọn mô hình màu muốn chuyển đổi (RGB, HSV, CMYK, v.v.).

### 3. Điều chỉnh tham số
- Sử dụng các thanh trượt để điều chỉnh các tham số của mô hình màu đã chọn.
- Mỗi mô hình màu sẽ có các tham số điều chỉnh khác nhau.

### 4. Xử lý hình ảnh
- Nhấp vào nút **"Convert"** để áp dụng các thay đổi và xử lý hình ảnh.

### 5. Xem kết quả
- Hình ảnh gốc và hình ảnh đã chuyển đổi sẽ được hiển thị song song để so sánh.
- Bạn có thể tải xuống hình ảnh đã xử lý bằng cách nhấp chuột phải và chọn "Save image as...".

## 🔍 Các mô hình màu được hỗ trợ

- **RGB (Red, Green, Blue)**: Mô hình màu cộng dùng cho hiển thị kỹ thuật số, mỗi pixel được biểu diễn bởi ba giá trị từ 0-255.
- **HSV (Hue, Saturation, Value)**: Biểu diễn màu theo góc màu (0-360°), độ bão hòa và giá trị (0-100%), phù hợp cho việc chọn màu.
- **HSL (Hue, Saturation, Lightness)**: Tương tự HSV nhưng với thông số độ sáng thay vì giá trị, giúp điều chỉnh độ sáng độc lập.
- **CMYK (Cyan, Magenta, Yellow, Key/Black)**: Mô hình màu trừ dùng trong in ấn, mỗi kênh màu có giá trị từ 0-100%.
- **YCbCr (Luminance, Chroma Blue, Chroma Red)**: Tách biệt thông tin độ sáng (Y) và màu sắc (Cb, Cr), thường dùng trong nén video/hình ảnh.
- **sRGB**: Tiêu chuẩn RGB được sử dụng phổ biến trên màn hình và web, được hiệu chuẩn với gamma 2.2.
- **Adobe RGB**: Không gian màu rộng hơn sRGB khoảng 35%, đặc biệt trong dải màu xanh lá-xanh dương, phát triển bởi Adobe năm 1998.
- **Grayscale**: Chuyển đổi hình ảnh sang thang độ xám, sử dụng công thức trọng số 0.299R + 0.587G + 0.114B để bảo toàn độ sáng cảm nhận.

## 📚 Tài liệu tham khảo

- [Color Models in Computer Graphics](https://en.wikipedia.org/wiki/Color_model)
- [OpenGL Shading Language](https://www.khronos.org/opengl/wiki/OpenGL_Shading_Language)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Digital Color Management: Encoding Solutions](https://www.wiley.com/en-us/Digital+Color+Management%3A+Encoding+Solutions%2C+2nd+Edition-p-9780470510490)

---

Phát triển bởi [Trần Đào Bá Thành] © 2025
