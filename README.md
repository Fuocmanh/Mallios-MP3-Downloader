# Mallios MP3 Downloader (v3.4)

Mallios là tiện ích mở rộng Chrome chuyên nghiệp dành cho Windows, giúp tải âm thanh chất lượng cao từ YouTube, YouTube Music, SoundCloud... và chuyển đổi thành MP3 320kbps siêu tốc. 

Hệ thống hoạt động với giao diện nút nổi thông minh trên trình duyệt kết hợp với máy chủ xử lý cục bộ Flask hiệu năng cao, hỗ trợ đồng bộ Google Drive và nghe thử nhạc tức thì.

> **Tuyên bố trách nhiệm:** Chỉ tải nội dung khi bạn có quyền tải, sử dụng hoặc lưu trữ nội dung đó. Bạn chịu trách nhiệm tuân thủ điều khoản dịch vụ của nền tảng nguồn và pháp luật hiện hành.

---

## ⭐ Tính năng nổi bật

- **Quét Playlist Tức Thì (0.001s):** Đọc trực tiếp danh sách bài hát từ bộ nhớ DOM của YouTube/YouTube Music trong chớp mắt mà không cần chờ nạp mạng.
- **Nghe Thử Nhạc Trực Tiếp (Direct 302 CDN Stream):** Chuyển hướng trực tiếp đến CDN tốc độ cao của Google, hỗ trợ phát âm thanh HTML5 và tua nhạc tùy thích không độ trễ.
- **Bộ nhớ RAM Cache Stream:** Lưu trữ luồng nghe thử vào bộ nhớ RAM, phát lại tức thì trong **0.01 giây**.
- **Tải Đa Luồng Song Song:** Tải đồng thời tối đa 5 bài hát với 8 luồng kết nối mỗi bài, hoàn tất chỉ trong vài giây.
- **Đồng Bộ Google Drive:** Tự động tải nhạc trực tiếp lên tài khoản Google Drive cá nhân qua OAuth 2.0.
- **Lọc Đoạn Thừa (SponsorBlock):** Tự động cắt bỏ các đoạn quảng cáo, intro, outro và nhạc nền thừa của video YouTube.
- **Chuẩn Hóa Tên Tệp & Chống Trùng Lặp:** Tự động tạo thư mục `Nghệ Sĩ/Tên Bài.mp3`, xóa dấu tiếng Việt, loại bỏ ký tự cấm Windows và tự động bỏ qua nếu bài hát đã có trên ổ cứng.
- **Khởi Động 1-Click Thông Minh (All-In-One):** Tệp `run.bat` tự động phát hiện, tải công cụ còn thiếu (`yt-dlp`, `ffmpeg`), cài đặt thư viện Python và bật máy chủ chỉ với 1 cú click chuột.

---

## 💻 Yêu cầu hệ thống

- **Hệ điều hành:** Windows 10 / 11 (64-bit).
- **Trình duyệt:** Bất kỳ trình duyệt nhân Chromium nào (Google Chrome, Microsoft Edge, Brave, Cốc Cốc, v.v.).
- **Quyền:** Chế độ dành cho nhà phát triển (Developer mode) trên trình duyệt.

---

## 🚀 Hướng dẫn cài đặt & Sử dụng (Chỉ 2 bước)

### Bước 1: Khởi động hệ thống
* Bấm đúp chuột vào file **`run.bat`** ở thư mục gốc.
* *(Lần đầu tiên chạy, hệ thống sẽ tự động tải `yt-dlp.exe`, `ffmpeg.exe`, thiết lập môi trường Python và bật máy chủ API `127.0.0.1:37491`).*

### Bước 2: Nạp Extension vào trình duyệt
1. Mở trình duyệt và truy cập trang quản lý tiện ích: `chrome://extensions` (hoặc `edge://extensions`, `coccoc://extensions`).
2. Bật công tắc **Chế độ dành cho nhà phát triển (Developer mode)** ở góc trên bên phải.
3. Nhấn nút **Tải tiện ích đã giải nén (Load unpacked)**.
4. Chọn thư mục **`extension`** trong thư mục dự án Mallios.

👉 **Hoàn tất!** Hãy mở YouTube hoặc YouTube Music, biểu tượng nút nổi Mallios sẽ xuất hiện ở góc màn hình sẵn sàng sử dụng.

---

## 📂 Cấu trúc thư mục dự án

```text
Mallios/
│
├── configs/                   📁 Tệp cấu hình, dữ liệu mẫu (.example.json) và lịch sử
│   ├── drive_config.json      (Cấu hình Google Drive OAuth Client)
│   ├── drive_config.example.json (Bản mẫu cấu hình Drive)
│   ├── drive_auth.json        (Token xác thực tài khoản Drive)
│   ├── history.json           (Lịch sử bài hát đã tải)
│   ├── history.example.json   (Bản mẫu lịch sử rỗng)
│   └── cookies.txt            (Tùy chọn: Cookie xác thực YouTube)
│
├── logs/                      📁 Nhật ký hệ thống
│   ├── error.log              (Ghi nhận lỗi tải & chuyển đổi)
│   └── startup.log            (Ghi nhận tiến trình khởi động)
│
├── downloads/                 📁 Thư mục lưu nhạc MP3 tải về mặc định
├── backend/                   📁 Mã nguồn API Flask, xử lý tải nhạc & Google Drive
├── extension/                 📁 Tiện ích Chrome Manifest V3 và giao diện UI
├── native-host/               📁 C# Native Messaging Host kết nối Extension và Server
├── scripts/                   📁 Bộ script cài đặt, biên dịch tự động
├── tools/                     📁 Chứa công cụ yt-dlp.exe, ffmpeg.exe (tự động tải)
│
├── run.bat                    🚀 Bộ khởi động thông minh All-In-One
├── install.bat                🛠️ Script cài đặt độc lập (nếu cần)
├── build.bat                  🔨 Biên dịch Native Host từ mã nguồn C#
├── requirements.txt           📦 Danh sách thư viện Python
├── README.md                  📖 Tài liệu giới thiệu dự án
└── FEATURES.md                ⭐ Chi tiết toàn bộ tính năng
```

---

## 🔒 Bảo mật & Dữ liệu riêng tư

- **Không chia sẻ thông tin nhạy cảm:** File `.gitignore` đã được cấu hình mặc định để **không bao giờ đẩy các file chứa token cá nhân** (`drive_auth.json`, `drive_config.json`, `cookies.txt`, `history.json`, `logs/`) lên Git.
- **Bảo vệ API Cục Bộ:** Máy chủ Flask chỉ lắng nghe duy nhất tại địa chỉ nội bộ `127.0.0.1:37491`, chặn toàn bộ các truy cập từ mạng bên ngoài.

---

## 🛠️ Khắc phục sự cố thường gặp

1. **Không kết nối được máy chủ:**
   * Hãy kiểm tra xem cửa sổ `run.bat` có đang mở không.
   * Nếu extension báo mất kết nối, hãy bấm nút Reload (Tải lại 🔄) tiện ích trong `chrome://extensions`.
2. **Không nghe thử được hoặc tải bị lỗi bản quyền:**
   * Hãy thử với video khác, hoặc xuất file `cookies.txt` từ trình duyệt đặt vào thư mục `configs/cookies.txt` để hỗ trợ các video giới hạn độ tuổi.
3. **Thư mục tải về không đúng vị trí:**
   * Nếu đường dẫn thư mục tùy chỉnh của bạn bị xóa hoặc không tồn tại, Mallios sẽ tự động lưu vào thư mục `Downloads` mặc định của Windows.
