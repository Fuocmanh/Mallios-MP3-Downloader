# Mallios MP3 Downloader (v3.6)

Mallios là tiện ích mở rộng Chrome chuyên nghiệp dành cho Windows, giúp tải âm thanh chất lượng cao từ YouTube, YouTube Music, SoundCloud... và chuyển đổi thành MP3 320kbps siêu tốc. 

Hệ thống hoạt động với kiến trúc **In-Memory RAM Streaming & Zero-Temp File** giúp xử lý toàn bộ dữ liệu tạm trên bộ nhớ RAM, bảo vệ ổ cứng, hỗ trợ đồng bộ Google Drive với cơ chế Auto-Retry thông minh, chia sẻ không dây sang điện thoại bằng mã QR và nghe thử nhạc tức thì.

> **Tuyên bố trách nhiệm:** Chỉ tải nội dung khi bạn có quyền tải, sử dụng hoặc lưu trữ nội dung đó. Bạn chịu trách nhiệm tuân thủ điều khoản dịch vụ của nền tảng nguồn và pháp luật hiện hành.

---

## ⭐ Tính năng nổi bật (v3.6)

- **🧠 Kiến Trúc In-Memory RAM Toàn Diện (Zero-Temp File):** Xử lý 100% dữ liệu raw, ảnh bìa, lọc `loudnorm` và nhúng ID3 trong bộ nhớ RAM ảo:
  * **Lưu Google Drive:** Đẩy trực tiếp từ RAM lên mây, tuyệt đối không ghi file rác vào ổ cứng máy tính.
  * **Lưu vào Máy tính:** Ghi duy nhất 1 lần file `.mp3` thành phẩm hoàn chỉnh, chấm dứt hoàn toàn lỗi file rác `.webp`, `.part` và lỗi khóa file `WinError 32` trên Windows.
- **☁️ Hàng Đợi Upload & Tự Động Thử Lại (Drive Auto-Retry):** Tự động bắt lỗi mạng `WinError 10060` / timeout và thử lại 3 lần với hàng đợi độc lập (tối đa 2 upload đồng thời) để bảo vệ Google Apps Script.
- **🛡️ Bộ Điều Tiết Bộ Nhớ Thông Minh (Smart Memory Guard):** Bài ngắn chạy 5 luồng (~50MB RAM), bài dài 1 tiếng tự điều tiết 1-2 luồng cuốn chiếu (~140MB - 280MB RAM), giải phóng RAM ngay khi hoàn thành.
- **Quét Playlist Tức Thì (0.001s):** Đọc trực tiếp danh sách bài hát từ bộ nhớ DOM của YouTube/YouTube Music trong chớp mắt mà không cần chờ nạp mạng.
- **🔍 Tìm Kiếm & Lọc Playlist Tức Thì:** Ô tìm kiếm thời gian thực giúp lọc nhanh bài hát theo tên hoặc nghệ sĩ, cùng nút chọn tất cả bài đang hiển thị.
- **Nghe Thử Nhạc Trực Tiếp (Direct 302 CDN Stream):** Chuyển hướng trực tiếp đến CDN tốc độ cao của Google, hỗ trợ phát âm thanh HTML5 và tua nhạc tùy thích không độ trễ.
- **🔁 Trình Phát Liên Tục & Điều Khiển Toàn Diện:** Tự động phát bài tiếp theo (Auto-play), cụm nút tua/chuyển bài ⏮/⏭, thanh chỉnh âm lượng 🔊 độc lập và hỗ trợ phím tắt (`Space`, `←`, `→`, `N`, `P`).
- **📱 Quét Mã QR Nghe / Tải Trên Điện Thoại:** Chia sẻ bài hát trực tiếp sang điện thoại cùng mạng Wi-Fi thông qua mã QR Code cục bộ không cần cắm dây cáp.
- **🖱️ Tải Siêu Tốc Bằng Chuột Phải (Context Menu):** Click chuột phải vào bất kỳ link video nào trên web ➔ Chọn `⚡ Tải MP3 bằng Mallios` để tải ngầm trong nền.
- **🎚️ Chuẩn Hóa Âm Lượng Đồng Đều (EBU R128):** Tích hợp bộ lọc âm thanh `loudnorm` giúp toàn bộ bài hát xuất ra có mức âm lượng chuẩn cân bằng 100%.
- **🖼️ Tự Động Nhúng Ảnh Bìa & Thẻ ID3 Metadata:** Tự động nhúng Thumbnail độ nét cao và thẻ ID3 (Tên bài, Ca sĩ, Album) vào file MP3.
- **✅ Huy Hiệu "Đã Có Trên Máy":** Tự động nhận diện bài hát đã tải và gắn huy hiệu màu xanh trong danh sách phát để tránh tải trùng.
- **🔔 Thông Báo Màn Hình Windows:** Gửi thông báo Toast khi hoàn tất tải nhạc.
- **🔄 Tự Động Cập Nhật `yt-dlp` Ngầm:** Tự động kiểm tra và nâng cấp bộ máy `yt-dlp.exe` lên phiên bản mới nhất khi khởi động.
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
├── backend/                   📁 Mã nguồn Python Flask API
│   ├── app.py                 (API xử lý chính, In-Memory RAM Streaming, Smart Memory Guard)
│   └── drive_service.py       (Dịch vụ Drive OAuth 2.0 & Apps Script với Auto-Retry 3 lần)
│
├── extension/                 📁 Tiện ích mở rộng Google Chrome (Manifest V3)
│   ├── manifest.json          (Cấu hình quyền, host permissions, context menus, notifications)
│   ├── background.js          (Service worker, quản lý kết nối native host & menu chuột phải)
│   ├── content/
│   │   ├── content.js         (Giao diện nút nổi, trích xuất DOM, trình phát âm thanh, QR code modal)
│   │   └── content.css        (Giao diện Dark Theme hiện đại, thanh volume, huy hiệu)
│   └── icons/                 (Biểu tượng ứng dụng)
│
├── native-host/               📁 Cầu nối Native Messaging Host cho Windows
│   ├── MalliosNativeHost.cs   (Mã nguồn C# .NET siêu nhẹ tự động bật server nền)
│   ├── install_host.bat       (Tự động biên dịch & đăng ký Registry Windows)
│   └── uninstall_host.bat     (Gỡ cài đặt Native Host)
│
├── scripts/                   📁 Tập lệnh tự động hóa cài đặt & kiểm thử
│   ├── setup-project.ps1      (Tự động tải yt-dlp, ffmpeg và cài đặt Python dependencies)
│   ├── convert_cookies.py     (Chuyển đổi cookie Netscape sang JSON)
│   └── test_*.py              (Bộ kiểm thử hiệu năng & chức năng)
│
├── tools/                     📁 Công cụ nhị phân (được run.bat tự động tải)
│   ├── yt-dlp.exe             (Bộ máy phân tích và trích xuất luồng media)
│   └── ffmpeg.exe             (Bộ mã hóa âm thanh sang MP3 chất lượng cao & loudnorm)
│
├── run.bat                    🚀 Khởi động hệ thống 1-click (Auto-setup + Auto-update)
├── README.md                  📖 Hướng dẫn cài đặt và sử dụng
└── FEATURES.md                🌟 Chi tiết toàn diện các tính năng kỹ thuật
```

---

## 📜 Giấy phép

Dự án được phân phối dưới giấy phép mã nguồn mở MIT.
