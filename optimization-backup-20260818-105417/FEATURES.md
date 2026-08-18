# Chi Tiết Tính Năng Mallios MP3 Downloader (v4.0)

Tài liệu này mô tả toàn diện và chi tiết tất cả các tính năng, kiến trúc kỹ thuật và cơ chế vận hành của hệ thống **Mallios MP3 Downloader**. Đây là quy chuẩn thiết kế để làm cơ sở cho mọi bản cập nhật và phát triển tính năng trong tương lai.

---

## 1. 🚀 Khởi Động Nền Không Cần Cửa Sổ (Native Messaging Host & Zero-Config)

- **Giao Tiếp Trực Tiếp (Native Messaging):** Tiện ích Chrome giao tiếp trực tiếp với một ứng dụng nhị phân C# nhỏ gọn (`MalliosNativeHost.exe`) trên Windows.
- **Tự Động Bật Máy Chủ:** Khi người dùng mở trình duyệt, tiện ích sẽ gửi tín hiệu khởi động ngầm máy chủ Python Flask ở chế độ nền (Background Process) hoàn toàn không hiện cửa sổ Command Prompt (Console).
- **Tự Động Nhận Diện Môi Trường Python (Multi-Environment Discovery):** Tự động dò tìm Python trong `.venv\Scripts\pythonw.exe`, `runtime\python\pythonw.exe` hoặc biến môi trường `PATH` của hệ thống. Đảm bảo ứng dụng luôn chạy ổn định trên bất kỳ máy Windows nào.
- **Hỗ trợ đa trình duyệt:** Hệ thống đăng ký Registry tự động hỗ trợ hoạt động trơn tru trên 6 trình duyệt Chromium phổ biến: Chrome, Edge, Brave, Cốc Cốc, Opera/Opera GX, Vivaldi.

---

## 2. 📂 Trình Chọn Thư Mục Thông Minh (Modern Explorer Folder Picker)

- **Giao diện chuẩn Windows Explorer (`IFileOpenDialog`):**
  * Tích hợp công cụ C# siêu nhẹ (`FolderPicker.exe`) sử dụng giao diện COM hiện đại `FOS_PICKFOLDERS` thay vì hộp thoại cây thư mục cũ kỹ.
  * Hộp thoại hiển thị đầy đủ thanh địa chỉ, ô tìm kiếm, thanh truy cập nhanh (Quick Access) và nút "Select Folder" rộng rãi.
- **Luôn Luôn Nổi Trên Cùng (TopMost / SetForegroundWindow):** Hộp thoại chọn thư mục được lập trình để tự động bật lên trên cùng mọi cửa sổ (kể cả trình duyệt Chrome), tránh hoàn toàn lỗi bị ẩn giấu dưới thanh Taskbar.
- **Tự Động Nhận Diện Thư Mục Tải Về:** Khi chạy lần đầu, tiện ích tự động dò tìm và điền sẵn đường dẫn thư mục `Downloads` mặc định của người dùng trên Windows. 

---

## 3. 🧠 Kiến Trúc In-Memory RAM Toàn Diện & Zero-Temp File

- **Xử lý 100% trên bộ nhớ RAM:** Toàn bộ quá trình tải dữ liệu raw từ YouTube, tải ảnh bìa Album, chuẩn hóa âm lượng `loudnorm` (EBU R128) và nhúng thẻ ID3 đều được thực hiện trực tiếp trong bộ nhớ RAM ảo (`io.BytesIO`).
- **Chế độ Lưu vào Google Drive (Cloud):** Dữ liệu âm thanh MP3 hoàn chỉnh được đẩy trực tiếp từ bộ nhớ RAM lên Google Drive thông qua hàm `upload_bytes_to_drive(...)`. Tuyệt đối không ghi file tạm.
- **Chế độ Lưu vào Máy tính (Local):** Ổ cứng chỉ thực hiện đúng 1 thao tác ghi file `.mp3` thành phẩm. Không bao giờ sinh ra file rác `.part`, `.webp`, thư mục tạm trên ổ cứng, **chấm dứt hoàn toàn lỗi khóa file trên Windows (`WinError 32` / `WinError 5`)**.

---

## 4. 🎵 Trình Nghe Thử Đa Chế Độ Siêu Tốc (Dual-Mode Preview Player)

- **Chế Độ YouTube IFrame API (Bypass Bot Detection):**
  * Ứng dụng tích hợp một trình phát YouTube ẩn (`youtube-nocookie.com/embed`) giao tiếp qua `postMessage`.
  * Nhờ tận dụng ngữ cảnh (context) đã đăng nhập của trình duyệt, nó vượt qua 100% các hệ thống chống Bot (ví dụ: `Sign in to confirm you're not a bot`) của YouTube.
  * Tốc độ phát lại cực nhanh: Dưới **0.1 giây** ngay khi bấm nút Nghe thử.
- **Chế Độ Âm Thanh Dự Phòng (HTML5 Audio Fallback):** Đối với các nền tảng khác (SoundCloud, hoặc phát nhạc từ file máy tính), hệ thống tự động chuyển đổi mượt mà sang thẻ `<audio>` truyền thống.
- **Đồng Bộ Giao Diện Hợp Nhất (Unified UI Sync):** Bất kể chạy ở chế độ IFrame hay HTML5, giao diện thanh tiến trình, nút Play/Pause, thời gian hiển thị và điều khiển âm lượng đều được đồng bộ hoàn hảo.

---

## 5. 🍪 Đồng Bộ Cookie Thông Minh (Auto-Sync Browser Cookies)

- Thay vì bắt người dùng trích xuất file `cookies.txt` thủ công, tiện ích sẽ tự động đọc Cookie trực tiếp từ miền `.youtube.com` thông qua quyền `chrome.cookies`.
- Tự động mã hóa Cookie sang định dạng chuẩn Netscape và đồng bộ về máy chủ Python để phục vụ quá trình tải nhạc (`yt-dlp`).
- Khắc phục hoàn toàn lỗi video giới hạn độ tuổi (Age-Restricted) và video yêu cầu tài khoản Premium.

---

## 6. 💿 Nút Nổi Dynamic Island (Floating UI)

- **Tự động gắn vào Mọi Nền Tảng:** Gắn nút nổi điều khiển vào YouTube, YouTube Music, SoundCloud, TikTok, Facebook.
- **Trạng Thái Chờ (Idle):** Biểu tượng nốt nhạc 🎵 nhỏ gọn, kéo thả tự do.
- **Trạng Thái Đang Phát (`.is-playing`):** Biến thành **Đĩa than xoay 360° vô tận** kèm vòng sóng âm Neon Ripple cực đẹp mắt.
- **Trạng Thái Hover (Dynamic Island):** Nút mở rộng mượt mà thành thanh Capsule 245px, hiển thị tên bài hát dạng cuộn Marquee, kèm nút `⏸` (Play/Pause) và `⏭` (Next Track) truy cập nhanh.
- **Vòng Tròn Tiến Độ SVG:** Khi đang tải, vòng viền ngoài hiển thị chính xác % tải thực tế, không ảnh hưởng đến chuyển động xoay của đĩa than.

---

## 7. 🎚️ Trình Phát Nhạc Chuẩn Spotify & Tính Năng Chuyên Sâu

- **Tốc độ phản hồi DOM Siêu Tốc:** Khởi tạo danh sách playlist hàng chục bài chỉ trong 0.001s bằng cách đọc trực tiếp các phần tử hiển thị DOM của YouTube.
- **Trộn Bài & Lặp Lại (Shuffle & Repeat):** 
  * Hỗ trợ lặp danh sách (🔁), lặp 1 bài (🔂).
  * Thuật toán Shuffle ghi nhớ lịch sử (Stack) giúp nút `⏮` (Previous) quay lại chính xác thứ tự bài hát ngẫu nhiên đã nghe.
- **Phím Tắt Toàn Diện (Keyboard Shortcuts):**
  * `Space`: Play/Pause
  * `←` / `→`: Tua nhanh 5s (`Shift` = 15s)
  * `N` / `P`: Chuyển bài kế tiếp / trước đó
  * `R` / `S` / `M`: Lặp bài, Trộn bài, Tắt/Mở tiếng
- **Điều Chỉnh Tốc Độ:** Nghe thử nhanh linh hoạt từ `0.75x` đến `2.0x`.
- **Độc Quyền Âm Thanh Tự Động:** Phát nhạc tại tab Nghe thử sẽ tự động Tạm dừng nhạc bên tab Lịch sử (và ngược lại), tránh chồng chéo âm thanh.

---

## 8. ☁️ Tối Ưu Tải Lên Google Drive & Auto-Retry Engine

- **Cơ chế Auto-Retry:** Bắt lỗi nghẽn mạng HTTP 5xx hoặc Timeout từ Google Apps Script và tự động thử lại tối đa 3 lần (với độ trễ tịnh tiến).
- **Hàng Đợi Semaphore Độc Lập (`DRIVE_UPLOAD_SEMAPHORE = 2`):** Chỉ cho phép tối đa 2 tác vụ tải lên Drive chạy cùng lúc để bảo vệ đường truyền, trong khi phần tải nhạc MP3 từ YouTube vẫn chạy max tốc độ (5-8 luồng).
- **Hỗ Trợ Video Dài (Smart Memory Guard):** Tự động cuốn chiếu luồng tải xuống còn 1-2 luồng cho các video dài (40 phút - 1 tiếng) để kiểm soát lượng RAM, chống sập ứng dụng.

---

## 9. 📱 Chia Sẻ Nhạc & Tải Nhanh Context Menu

- **Chia Sẻ File Qua QR Code LAN:** Người dùng có thể nghe hoặc tải bài hát trên điện thoại (chung mạng Wi-Fi) thông qua việc quét mã QR ngay trong trình quản lý lịch sử.
- **Trình Đơn Chuột Phải (Context Menu):** Click chuột phải vào video hoặc link trên web bất kỳ ➔ Bấm `⚡ Tải MP3 bằng Mallios` để kích hoạt ngầm quá trình tải ngay lập tức.
- **Chuẩn Hóa Âm Lượng Đồng Đều (EBU R128):** Sử dụng bộ lọc FFmpeg `loudnorm` để đồng bộ âm lượng toàn bộ các bài hát xuất ra ở một mức chuẩn nhất định, chống chói tai.
- **Làm Sạch Tên & Cấu Trúc File:** Mọi tệp xuất ra luôn được loại bỏ dấu Tiếng Việt, loại bỏ ký tự cấm của Windows, tạo thành cấu trúc file chuẩn `Nghệ Sĩ / Tên Bài Hát.mp3`.

---
*Tài liệu này áp dụng cho quy chuẩn tính năng từ Phiên bản 4.0.*
