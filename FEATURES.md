# Chi Tiết Tính Năng Mallios MP3 Downloader (v3.6)

Tài liệu này mô tả toàn diện và chi tiết tất cả các tính năng, kiến trúc kỹ thuật và cơ chế vận hành của hệ thống **Mallios MP3 Downloader**.

---

## 1. Kiến Trúc In-Memory RAM Toàn Diện & Zero-Temp File

- **Xử lý 100% trên bộ nhớ RAM:**
  * Toàn bộ quá trình tải dữ liệu raw từ YouTube, tải ảnh bìa Album, chuẩn hóa âm lượng `loudnorm` (EBU R128) và nhúng thẻ ID3 đều được thực hiện trực tiếp trong bộ nhớ RAM ảo (`io.BytesIO`).
- **Chế độ Lưu vào Google Drive (Cloud):**
  * Dữ liệu âm thanh MP3 hoàn chỉnh được đẩy trực tiếp từ bộ nhớ RAM lên Google Drive thông qua hàm `upload_bytes_to_drive(...)`.
  * Tuyệt đối **không ghi bất kỳ 1 byte dữ liệu nào vào ổ cứng máy tính**, RAM tự động thu hồi sạch sẽ ngay sau khi upload xong.
- **Chế độ Lưu vào Máy tính (Local):**
  * Ổ cứng chỉ thực hiện **đúng 1 thao tác ghi file `.mp3` thành phẩm** vào thư mục chuẩn `[Nghệ Sĩ]/[Tên Bài Không Dấu].mp3`.
  * Không bao giờ sinh ra file rác `.part`, `.webp`, `.webm` hay thư mục tạm trên ổ cứng, **chấm dứt hoàn toàn lỗi khóa file trên Windows (`WinError 32` / `WinError 5`)**.

---

## 2. Tối Ưu Upload Google Drive & Tự Động Thử Lại (Auto-Retry Engine)

- **Cơ chế Auto-Retry với Exponential Backoff:**
  * Tự động phát hiện lỗi nghẽn mạng `WinError 10060`, `TimeoutError` hoặc lỗi máy chủ HTTP 500/502/503/504 từ Google Apps Script và tự động thử lại tối đa 3 lần ($2\text{s} \rightarrow 4\text{s} \rightarrow 8\text{s}$).
- **Hàng đợi Upload độc lập (`DRIVE_UPLOAD_SEMAPHORE = 2`):**
  * Giới hạn tối đa 2 bài upload Google Drive đồng thời để tránh làm quá tải máy chủ Google Apps Script, trong khi các luồng tải YouTube vẫn chạy với tốc độ tối đa.
- **Tăng Timeout lên 180s:** Cho phép tiếp nhận và ghi trọn vẹn các file âm thanh siêu dài (40 phút - 1 tiếng) mà không bị ngắt kết nối.

---

## 3. Bộ Điều Tiết Bộ Nhớ Thông Minh (Smart Memory Guard)

- **Kiểm soát dung lượng RAM chặt chẽ:**
  * **Bài hát thông thường (< 15 phút):** Chạy tối đa 3–5 luồng song song, tiêu thụ chỉ khoảng **`50MB – 80MB RAM`**.
  * **Video dài (40 phút – 1 tiếng):** Tự động điều tiết xuống 1–2 luồng cuốn chiếu để khóa mức RAM an toàn ở mức **`140MB – 280MB`**.
- **Giải phóng tức thì:** Ngay khi một bài hát hoàn tất lưu trữ, bộ nhớ RAM của bài đó được dọn dẹp và thu hồi ngay lập tức (`gc.collect()`).

---

## 4. Giao diện nút nổi thông minh (Floating UI)

- **Đa nền tảng hỗ trợ:** Tự động chèn giao diện tiện ích vào YouTube, YouTube Music, SoundCloud, TikTok, Facebook, Instagram.
- **Kéo thả tùy biến vị trí:** Người dùng có thể kéo thả nút Mallios đến bất kỳ vị trí nào trên màn hình. Tọa độ được ghi nhớ độc lập theo từng tên miền thông qua `localStorage`.
- **Tự động căn chỉnh thông minh:** Khi bấm mở bảng điều khiển, cửa sổ popup sẽ tự động tính toán góc màn hình (trên/dưới/trái/phải) để hiển thị trọn vẹn, không bao giờ bị tràn ra ngoài khung nhìn trình duyệt.
- **3 Tab chức năng chính:**
  1. **Tải nhanh (Quick Download):** Tải ngay video/bài hát đang phát với tùy chọn chất lượng và số lượng bài.
  2. **Chọn bài (Playlist Selector):** Quét danh sách phát, nghe thử trực tiếp, tìm kiếm/lọc bài hát tức thì và chọn tải từng bài cụ thể.
  3. **Lịch sử (History Manager):** Quản lý bài đã tải, phát liên tục toàn bộ danh sách, chia sẻ qua mã QR sang điện thoại, mở thư mục chứa tệp và xem liên kết Google Drive.

---

## 5. Trích xuất Playlist Siêu Tốc (Instant DOM Scraper - 0.001s)

- **Cơ chế đọc trực tiếp từ DOM:** Khi người dùng mở danh sách phát trên YouTube hoặc YouTube Music, tiện ích sẽ đọc trực tiếp dữ liệu bài hát từ bộ nhớ giao diện DOM (`ytd-playlist-panel-video-renderer`, `ytmusic-responsive-list-item-renderer`, `ytd-playlist-video-renderer`).
- **Tốc độ phản hồi tức thì:** Danh sách 10 đến 100+ bài hát hiển thị lên bảng điều khiển chỉ trong **`0.001 giây`** (chớp mắt) mà không cần gửi yêu cầu mạng hay chờ máy chủ phân tích.
- **Cơ chế dự phòng (Server Fallback):** Nếu không đọc được từ DOM (ví dụ URL playlist tổng quát dạng link), hệ thống sẽ tự động gọi API `/get-playlist` phía Flask server để phân tích nhanh danh sách bằng `yt-dlp` flat-playlist.
- **🔍 Bộ lọc tìm kiếm trực tiếp (Live Search):** Ô tìm kiếm thời gian thực giúp lọc nhanh bài hát theo tên hoặc nghệ sĩ trong tích tắc, hỗ trợ nút *Chọn tất cả bài đang hiển thị*.
- **✅ Huy hiệu nhận diện bài đã tải (Duplicate Badge):** Tự động quét và gắn huy hiệu `✅ Đã có` màu xanh cho các bài hát đã tồn tại trên máy hoặc trong lịch sử tải để tránh tải trùng lặp.

---

## 6. Trình Phát Âm Thanh Hiện Đại & Nghe Thử Siêu Tốc (Preview & Continuous Player < 1s)

- **Giải Mã Stream In-Process Siêu Tốc (< 1s):**
  * Tích hợp trực tiếp module `yt_dlp` in-process trong máy chủ Python thay vì khởi chạy tiến trình con `yt-dlp.exe`.
  * Giảm thời gian trích xuất âm thanh từ **3.5s xuống dưới 0.8s**.
- **Client-Side Map Cache & Endpoint `/api/preview-info`:**
  * Endpoint `/api/preview-info` cung cấp trực tiếp luồng stream CDN cho Extension.
  * Extension lưu đệm vào `Map Cache` tại Client, giúp phát ngay lập tức trong **`0.01 - 0.05 giây`** mà không cần đợi vòng chuyển tiếp mạng.
- **Bộ nhớ RAM Cache Stream 4 Giờ (`PREVIEW_STREAM_CACHE`):**
  * Lưu trữ đường dẫn stream vào RAM cache máy chủ trong 4 giờ. Phản hồi phát lại tức thì trong **`0.00 giây`**.
- **Nạp trước thông minh đa tầng (Multi-tier Smart Prefetching):**
  * Tự động nạp trước song song (8 Workers) danh sách bài hát ngay khi quét danh sách.
  * Tự động nạp trước khi rê chuột (`mouseenter`) hoặc khi đang phát bài kế bên (`N+1`, `N+2`, `N-1`).
- **🔁 Tự động phát liên tục (Auto-play & Navigation):**
  * Hỗ trợ tự động chuyển bài tiếp theo khi hết bài ở cả tab **Chọn bài** và tab **Lịch sử**.
  * Cụm nút điều hướng tiện lợi: **⏮ Bài trước**, **▶/⏸ Phát/Tạm dừng**, **⏭ Bài tiếp theo**.
- **🔊 Điều chỉnh âm lượng & Tắt tiếng (Volume Slider):** Thanh trượt chỉnh âm lượng độc lập cho trình phát, ghi nhớ mức âm lượng vào `localStorage`.
- **⌨️ Phím tắt điều khiển nhanh (Keyboard Shortcuts):**
  * `Space`: Phát / Tạm dừng bài hát.
  * `←` / `→`: Tua lùi / Tua tới 5 giây.
  * `N` / `P`: Chuyển bài kế tiếp / bài trước đó.

---

## 7. 📱 Chia Sẻ Nhạc Không Dây Sang Điện Thoại (Local Wi-Fi QR Code Share)

- Trong tab **Lịch sử**, bên cạnh mỗi bài hát có nút **`📱 QR`**.
- Khi bấm vào, một hộp thoại sẽ hiện ra kèm **Mã QR** chứa liên kết phát/tải trực tiếp qua địa chỉ IP nội bộ của máy tính (`http://192.168.x.x:37491/...`).
- Bạn chỉ cần dùng camera điện thoại (cùng kết nối Wi-Fi) để quét mã là có thể nghe hoặc tải thẳng file MP3 về điện thoại mà không cần cắm cáp kết nối!

---

## 8. 🖱️ Tải Nhanh 1-Click Bằng Menu Chuột Phải (Context Menu Integration)

- Tiện ích tích hợp trực tiếp vào menu chuột phải của trình duyệt: **`⚡ Tải MP3 bằng Mallios`**.
- Khi lướt web trên YouTube, Facebook, TikTok, bạn chỉ cần click chuột phải vào bất kỳ liên kết video hoặc trang video nào ➔ Chọn lệnh tải.
- Tiến trình tải sẽ được kích hoạt ngầm tự động trong nền và thông báo khi hoàn tất mà không cần phải mở cửa sổ tiện ích.

---

## 9. 🎚️ Chuẩn Hóa Âm Lượng Đồng Đều (Loudness Normalization - EBU R128)

- Tích hợp bộ lọc âm thanh `loudnorm` (`I=-16:TP=-1.5:LRA=11`) của FFmpeg vào quy trình chuyển đổi MP3.
- Mọi bài hát tải về từ các nguồn khác nhau đều có mức âm lượng chuẩn đồng đều, loại bỏ hoàn toàn tình trạng bài quá nhỏ hoặc bài quá to gây chói tai khi nghe trên tai nghe hoặc loa ô tô.

---

## 10. 🖼️ Tự Động Nhúng Ảnh Bìa (Cover Art) & Thẻ ID3 Metadata

- Tự động tải về ảnh đại diện chất lượng cao (Thumbnail) của video và nhúng trực tiếp làm ảnh bìa Album (Cover Art) của file MP3.
- Nhúng đầy đủ thẻ thông tin ID3v2 (Tên bài hát, Tên nghệ sĩ/Kênh, Album, Năm phát hành) giúp các phần mềm nghe nhạc hiển thị đẹp mắt và đầy đủ thông tin.

---

## 11. 🔄 Tự Động Cập Nhật `yt-dlp` Ngầm (Auto-Update Engine)

- Khi máy chủ khởi động qua `run.bat` hoặc chạy nền, hệ thống sẽ tự động chạy lệnh kiểm tra và cập nhật `yt-dlp.exe` lên phiên bản mới nhất từ kho lưu trữ GitHub chính thức.
- Đảm bảo ứng dụng luôn luôn tương thích với các thay đổi mới nhất từ YouTube mà không bao giờ bị lỗi out-date.

---

## 12. Cơ Chế Làm Sạch Tên Tệp & Bảo Toàn Cấu Trúc Đĩa

- **Cấu trúc lưu trữ chuẩn:** `[Thư Mục Lưu]/[Tên Nghệ Sĩ]/[Tên Bài Hát].mp3`
- **Xóa dấu tiếng Việt 100%:** Loại bỏ toàn bộ dấu thanh tiếng Việt (ví dụ: `Sơn Tùng M-TP/Âm Thầm Bên Em.mp3` ➔ `Son Tung M-TP/Am Tham Ben Em.mp3`).
- **Khử bỏ ký tự cấm trên Windows:** Tự động loại bỏ các ký tự `\ / : * ? " < > |`.
