# Mallios MP3 Downloader (v4.0)

Mallios là tiện ích mở rộng Chrome chuyên nghiệp dành cho Windows, giúp tải âm thanh chất lượng cao từ YouTube, YouTube Music, SoundCloud... và chuyển đổi thành MP3 320kbps siêu tốc. 

Hệ thống hoạt động với kiến trúc **In-Memory RAM Streaming & Zero-Temp File** giúp xử lý toàn bộ dữ liệu tạm trên bộ nhớ RAM, bảo vệ ổ cứng, hỗ trợ đồng bộ Google Drive với cơ chế Auto-Retry thông minh, chia sẻ không dây sang điện thoại bằng mã QR, nghe thử nhạc tức thì (**< 0.1s**) và **Nút nổi Dynamic Island** thông minh.

> **Tuyên bố trách nhiệm:** Chỉ tải nội dung khi bạn có quyền tải, sử dụng hoặc lưu trữ nội dung đó. Bạn chịu trách nhiệm tuân thủ điều khoản dịch vụ của nền tảng nguồn và pháp luật hiện hành.

---

## ⭐ Tính năng nổi bật (v4.0)

- **🚀 Khởi Động Nền Siêu Tốc (Native Messaging Host):** 
  * Tự động khởi động ngầm máy chủ Python ngay khi trình duyệt mở mà không cần cửa sổ dòng lệnh đen (Zero-Config). 
  * Hỗ trợ tự động nhận diện đa môi trường Python trên toàn bộ 6 trình duyệt Chromium phổ biến (Chrome, Edge, Brave, Cốc Cốc, Opera, Vivaldi).
- **📂 Trình Chọn Thư Mục Thông Minh (`FolderPicker.exe`):**
  * Giao diện chuẩn Windows Explorer hiện đại (IFileOpenDialog) với thanh địa chỉ, ô tìm kiếm, thanh truy cập nhanh và nút Select Folder rộng rãi.
  * Tự động nổi lên trên cùng (TopMost), chấm dứt hoàn toàn tình trạng bị ẩn sau Chrome.
- **🎵 Trình Nghe Thử Đa Chế Độ Tức Thì (Dual-Mode Player):**
  * Chế độ YouTube IFrame: Tốc độ phản hồi < 0.1s, bypass hoàn toàn hệ thống chống Bot nhờ sử dụng ngữ cảnh bảo mật của người dùng trên trình duyệt.
  * Chế độ Audio dự phòng cho SoundCloud & máy tính, đồng bộ hoàn hảo giao diện (UI Sync).
- **🍪 Đồng Bộ Cookie Tự Động (Auto-Sync Cookies):** Tự động bắt và giải mã cookie từ trình duyệt về máy chủ Python để tải nhạc, loại bỏ hoàn toàn rào cản từ YouTube (Age-Restricted, Premium).
- **💿 Nút Nổi Thông Minh Dynamic Island (Apple & Spotify Style):**
  * **Đĩa Than Xoay 360° (`💿`):** Tự động chuyển đổi sang đĩa than quay đều theo nhịp bài hát khi đang phát nhạc.
  * **Sóng Âm Ripple Neon:** Hiệu ứng sóng âm phát sáng dịu mắt lan tỏa xung quanh nút nổi.
  * **Dynamic Island Capsule trên Hover:** Tự động mở rộng thành thanh điều khiển thu nhỏ khi rê chuột, cho phép Play/Pause `⏸` và Next `⏭` trực tiếp.
  * **Vòng Tròn Tiến Độ SVG:** Viền ngoài nút nổi hiển thị trực quan tiến độ tải `%` thực tế.
- **🧠 Kiến Trúc In-Memory RAM Toàn Diện (Zero-Temp File):** Xử lý 100% dữ liệu raw, ảnh bìa, lọc `loudnorm` và nhúng ID3 trong bộ nhớ RAM ảo:
  * **Lưu Google Drive:** Đẩy trực tiếp từ RAM lên mây, tuyệt đối không ghi file rác vào ổ cứng máy tính.
  * **Lưu vào Máy tính:** Ghi duy nhất 1 lần file `.mp3` thành phẩm hoàn chỉnh, chấm dứt hoàn toàn lỗi khóa file `WinError 32` trên Windows.
- **☁️ Hàng Đợi Upload & Tự Động Thử Lại (Drive Auto-Retry):** Tự động bắt lỗi mạng và thử lại 3 lần với hàng đợi độc lập (tối đa 2 upload đồng thời) để bảo vệ Google Apps Script.
- **🛡️ Bộ Điều Tiết Bộ Nhớ Thông Minh (Smart Memory Guard):** Bài ngắn chạy 5 luồng (~50MB RAM), bài dài 1 tiếng tự điều tiết 1-2 luồng cuốn chiếu (~140MB - 280MB RAM), giải phóng RAM ngay khi hoàn thành.
- **⚡ Quét Playlist Tức Thì (0.001s):** Đọc trực tiếp danh sách bài hát từ bộ nhớ DOM của YouTube/YouTube Music trong chớp mắt mà không cần chờ mạng.
- **🎵 Trình Phát Nghe Thử Chuẩn Spotify (Spotify-Style Pro Player):**
  * **Chế độ Lặp 3 nấc:** `🔁 Lặp toàn bộ`, `🔂 Lặp 1 bài`, `➡️ Không lặp`.
  * **Trộn bài thông minh (Smart Shuffle `🔀`):** Phát ngẫu nhiên có ghi nhớ lịch sử quay lại bài trước (`⏮`).
  * **Tùy chỉnh tốc độ phát (`⚡ 0.75x - 2.0x`):** Điều chỉnh tốc độ nghe thử linh hoạt.
  * **Thanh tua nhạc trực quan & Hover Tooltip:** Xem trước thời gian phút:giây khi rê chuột.
- **📱 Quét Mã QR Nghe / Tải Trên Điện Thoại:** Chia sẻ bài hát trực tiếp sang điện thoại cùng mạng Wi-Fi thông qua mã QR Code cục bộ không cần cắm dây cáp.
- **🖱️ Tải Siêu Tốc Bằng Chuột Phải (Context Menu):** Click chuột phải vào bất kỳ link video nào trên web ➔ Chọn `⚡ Tải MP3 bằng Mallios` để tải ngầm trong nền.
- **🎚️ Chuẩn Hóa Âm Lượng Đồng Đều (EBU R128):** Tích hợp bộ lọc âm thanh `loudnorm` giúp toàn bộ bài hát xuất ra có mức âm lượng chuẩn cân bằng 100%.

---

## 💻 Yêu cầu hệ thống

- **Hệ điều hành:** Windows 10 / 11 (64-bit).
- **Trình duyệt:** Bất kỳ trình duyệt nhân Chromium nào (Google Chrome, Microsoft Edge, Brave, Cốc Cốc, v.v.).
- **Quyền:** Chế độ dành cho nhà phát triển (Developer mode) trên trình duyệt.

---

## 🚀 Hướng dẫn cài đặt & Sử dụng

### Cài Đặt Khởi Tạo (Lần Đầu Tiên)
1. Bấm đúp chuột vào file **`run.bat`** ở thư mục gốc. Hệ thống sẽ tự động cấu hình môi trường Python, tải `yt-dlp.exe`, `ffmpeg.exe` và biên dịch bộ điều khiển C#.

### Nạp Extension vào trình duyệt
1. Mở trình duyệt và truy cập trang quản lý tiện ích: `chrome://extensions` (hoặc `edge://extensions`, `coccoc://extensions`).
2. Bật công tắc **Chế độ dành cho nhà phát triển (Developer mode)** ở góc trên bên phải.
3. Nhấn nút **Tải tiện ích đã giải nén (Load unpacked)**.
4. Chọn thư mục **`extension`** trong thư mục dự án Mallios.

👉 **Hoàn tất vô hình (Zero-Config):** Từ nay về sau, bạn **không cần phải chạy `run.bat`** nữa. Chỉ cần bật trình duyệt, máy chủ API sẽ tự động khởi chạy ngầm 100% trong nền. Biểu tượng Mallios sẽ luôn chực chờ trên YouTube / SoundCloud.

---

## 📂 Cấu trúc thư mục dự án

```text
Mallios/
│
├── configs/                   📁 Tệp cấu hình, dữ liệu mẫu (.example.json) và lịch sử
│   ├── drive_config.json      (Cấu hình Google Drive OAuth Client)
│   ├── history.json           (Lịch sử bài hát đã tải)
│   └── cookies.txt            (Tự động đồng bộ Cookie YouTube)
│
├── backend/                   📁 Mã nguồn Python Flask API
│   ├── app.py                 (API xử lý chính, In-Memory RAM Streaming, Smart Memory Guard)
│   └── drive_service.py       (Dịch vụ Drive OAuth 2.0 & Apps Script với Auto-Retry 3 lần)
│
├── extension/                 📁 Tiện ích mở rộng Google Chrome (Manifest V3)
│   ├── background.js          (Service worker, quản lý kết nối native host & menu chuột phải)
│   └── content/
│       ├── content.js         (Giao diện nút nổi, trích xuất DOM, trình phát YouTube IFrame API)
│       └── content.css        (Giao diện Dark Theme hiện đại, thanh volume, huy hiệu)
│
├── native-host/               📁 Cầu nối Native Messaging Host cho Windows
│   ├── MalliosNativeHost.cs   (Mã nguồn C# tự động bật/tắt server Python ẩn nền)
│   └── install_host.bat       (Tự động biên dịch & đăng ký Registry Windows cho 6 trình duyệt)
│
├── scripts/                   📁 Tập lệnh tự động hóa cài đặt
│   └── setup-project.ps1      (Tự động tải công cụ và biên dịch FolderPicker)
│
├── tools/                     📁 Công cụ nhị phân
│   ├── FolderPicker.cs / exe  (Trình chọn thư mục COM IFileOpenDialog nổi trên cùng)
│   ├── yt-dlp.exe             (Bộ máy phân tích và trích xuất luồng media)
│   └── ffmpeg.exe             (Bộ mã hóa âm thanh sang MP3 chất lượng cao & loudnorm)
│
├── run.bat                    🚀 Khởi động hệ thống & Cài đặt tự động
├── README.md                  📖 Hướng dẫn cài đặt và sử dụng
└── FEATURES.md                🌟 Chi tiết toàn diện các tính năng kỹ thuật
```

---

## 📜 Giấy phép

Dự án được phân phối dưới giấy phép mã nguồn mở MIT.
