# Chi Tiết Tính Năng Mallios MP3 Downloader (v3.5)

Tài liệu này mô tả toàn diện và chi tiết tất cả các tính năng, kiến trúc kỹ thuật và cơ chế vận hành của hệ thống **Mallios MP3 Downloader**.

---

## 1. Giao diện nút nổi thông minh (Floating UI)

- **Đa nền tảng hỗ trợ:** Tự động chèn giao diện tiện ích vào YouTube, YouTube Music, SoundCloud, TikTok, Facebook, Instagram.
- **Kéo thả tùy biến vị trí:** Người dùng có thể kéo thả nút Mallios đến bất kỳ vị trí nào trên màn hình. Tọa độ được ghi nhớ độc lập theo từng tên miền thông qua `localStorage`.
- **Tự động căn chỉnh thông minh:** Khi bấm mở bảng điều khiển, cửa sổ popup sẽ tự động tính toán góc màn hình (trên/dưới/trái/phải) để hiển thị trọn vẹn, không bao giờ bị tràn ra ngoài khung nhìn trình duyệt.
- **3 Tab chức năng chính:**
  1. **Tải nhanh (Quick Download):** Tải ngay video/bài hát đang phát với tùy chọn chất lượng và số lượng bài.
  2. **Chọn bài (Playlist Selector):** Quét danh sách phát, nghe thử trực tiếp, tìm kiếm/lọc bài hát tức thì và chọn tải từng bài cụ thể.
  3. **Lịch sử (History Manager):** Quản lý bài đã tải, phát liên tục toàn bộ danh sách, chia sẻ qua mã QR sang điện thoại, mở thư mục chứa tệp và xem liên kết Google Drive.

---

## 2. Trích xuất Playlist Siêu Tốc (Instant DOM Scraper - 0.001s)

- **Cơ chế đọc trực tiếp từ DOM:** Khi người dùng mở danh sách phát trên YouTube hoặc YouTube Music, tiện ích sẽ đọc trực tiếp dữ liệu bài hát từ bộ nhớ giao diện DOM (`ytd-playlist-panel-video-renderer`, `ytmusic-responsive-list-item-renderer`, `ytd-playlist-video-renderer`).
- **Tốc độ phản hồi tức thì:** Danh sách 10 đến 100+ bài hát hiển thị lên bảng điều khiển chỉ trong **`0.001 giây`** (chớp mắt) mà không cần gửi yêu cầu mạng hay chờ máy chủ phân tích.
- **Cơ chế dự phòng (Server Fallback):** Nếu không đọc được từ DOM (ví dụ URL playlist tổng quát dạng link), hệ thống sẽ tự động gọi API `/get-playlist` phía Flask server để phân tích nhanh danh sách bằng `yt-dlp` flat-playlist.
- **🔍 Bộ lọc tìm kiếm trực tiếp (Live Search):** Ô tìm kiếm thời gian thực giúp lọc nhanh bài hát theo tên hoặc nghệ sĩ trong tích tắc, hỗ trợ nút *Chọn tất cả bài đang hiển thị*.
- **✅ Huy hiệu nhận diện bài đã tải (Duplicate Badge):** Tự động quét và gắn huy hiệu `✅ Đã có` màu xanh cho các bài hát đã tồn tại trên máy hoặc trong lịch sử tải để tránh tải trùng lặp.

---

## 3. Trình Phát Âm Thanh Hiện Đại & Nghe Thử Siêu Tốc (Preview & Continuous Player)

- **Chuyển hướng trực tiếp Google CDN (HTTP 302 Redirect):**
  * Route API `/api/preview-stream` trích xuất luồng audio trực tiếp từ YouTube (`ba/18/b` android client) và phản hồi mã **`HTTP 302 Redirect`** trực tiếp đến cụm máy chủ Googlevideo CDN tốc độ cao.
  * Trình duyệt kết nối trực tiếp với CDN của Google, giúp phát nhạc với băng thông mạng tối đa và không tiêu tốn RAM của máy tính.
- **Bộ nhớ RAM Cache Stream (`PREVIEW_STREAM_CACHE`):**
  * Lưu trữ đường dẫn stream vào RAM cache trong 30 phút. Phản hồi phát lại tức thì trong **`0.01 giây`**.
- **🔁 Tự động phát liên tục (Auto-play & Navigation):**
  * Hỗ trợ tự động chuyển bài tiếp theo khi hết bài ở cả tab **Chọn bài** và tab **Lịch sử**.
  * Cụm nút điều hướng tiện lợi: **⏮ Bài trước**, **▶/⏸ Phát/Tạm dừng**, **⏭ Bài tiếp theo**.
- **🔊 Điều chỉnh âm lượng & Tắt tiếng (Volume Slider):** Thanh trượt chỉnh âm lượng độc lập cho trình phát, ghi nhớ mức âm lượng vào `localStorage`.
- **⌨️ Phím tắt điều khiển nhanh (Keyboard Shortcuts):**
  * `Space`: Phát / Tạm dừng bài hát.
  * `←` / `→`: Tua lùi / Tua tới 5 giây.
  * `N` / `P`: Chuyển bài kế tiếp / bài trước đó.

---

## 4. 📱 Chia Sẻ Nhạc Không Dây Sang Điện Thoại (Local Wi-Fi QR Code Share)

- Trong tab **Lịch sử**, bên cạnh mỗi bài hát có nút **`📱 QR`**.
- Khi bấm vào, một hộp thoại sẽ hiện ra kèm **Mã QR** chứa liên kết phát/tải trực tiếp qua địa chỉ IP nội bộ của máy tính (`http://192.168.x.x:37491/...`).
- Bạn chỉ cần dùng camera điện thoại (cùng kết nối Wi-Fi) để quét mã là có thể nghe hoặc tải thẳng file MP3 về điện thoại mà không cần cắm cáp kết nối!

---

## 5. 🖱️ Tải Nhanh 1-Click Bằng Menu Chuột Phải (Context Menu Integration)

- Tiện ích tích hợp trực tiếp vào menu chuột phải của trình duyệt: **`⚡ Tải MP3 bằng Mallios`**.
- Khi lướt web trên YouTube, Facebook, TikTok, bạn chỉ cần click chuột phải vào bất kỳ liên kết video hoặc trang video nào ➔ Chọn lệnh tải.
- Tiến trình tải sẽ được kích hoạt ngầm tự động trong nền và thông báo khi hoàn tất mà không cần phải mở cửa sổ tiện ích.

---

## 6. 🎚️ Chuẩn Hóa Âm Lượng Đồng Đều (Loudness Normalization - EBU R128)

- Tích hợp bộ lọc âm thanh `loudnorm` (`I=-16:TP=-1.5:LRA=11`) của FFmpeg vào quy trình chuyển đổi MP3.
- Mọi bài hát tải về từ các nguồn khác nhau đều có mức âm lượng chuẩn đồng đều, loại bỏ hoàn toàn tình trạng bài quá nhỏ hoặc bài quá to gây chói tai khi nghe trên tai nghe hoặc loa ô tô.

---

## 7. 🖼️ Tự Động Nhúng Ảnh Bìa (Cover Art) & Thẻ ID3 Metadata

- Tự động tải về ảnh đại diện chất lượng cao (Thumbnail) của video và nhúng trực tiếp làm ảnh bìa Album (Cover Art) của file MP3.
- Nhúng đầy đủ thẻ thông tin ID3v2 (Tên bài hát, Tên nghệ sĩ/Kênh, Album, Năm phát hành) giúp các phần mềm nghe nhạc hiển thị đẹp mắt và đầy đủ thông tin.

---

## 8. 🔄 Tự Động Cập Nhật `yt-dlp` Ngầm (Auto-Update Engine)

- Khi máy chủ khởi động qua `run.bat` hoặc chạy nền, hệ thống sẽ tự động chạy lệnh kiểm tra và cập nhật `yt-dlp.exe` lên phiên bản mới nhất từ kho lưu trữ GitHub chính thức.
- Đảm bảo ứng dụng luôn luôn tương thích với các thay đổi mới nhất từ YouTube mà không bao giờ bị lỗi out-date.

---

## 9. ☁️ Cô Lập Thư Mục Tạm & Dọn Dẹp Hoàn Toàn Khi Lưu Google Drive

- Khi người dùng chọn chế độ **Lưu vào Google Drive**, toàn bộ quá trình tải về và chuyển đổi MP3 trung gian được chuyển sang thư mục tạm cô lập `.temp_drive/`.
- Tự động xóa sạch 100% các file và thư mục tạm ngay sau khi hoàn tất tải lên Google Drive (hoặc khi có sự cố), đảm bảo **không bao giờ để lại file rác hoặc thư mục trống trên máy tính**.

---

## 10. 🔔 Thông Báo Màn Hình Windows (Chrome Desktop Notifications)

- Tích hợp hệ thống thông báo Toast của Windows thông qua Chrome Notifications API.
- Khi hoàn tất lượt tải đơn hoặc danh sách bài hát, một thông báo sinh động sẽ xuất hiện ở góc dưới màn hình máy tính để người dùng biết ngay kết quả.

---

## 11. Cơ Chế Tải Đa Luồng Song Song (Parallel Downloader)

- **Tối đa 5 bài hát đồng thời:** Backend sử dụng `ThreadPoolExecutor` để tải đồng thời tối đa 5 bài hát song song.
- **Đa luồng kết nối cho từng bài (`-N 8`):** Mỗi tiến trình `yt-dlp` được cấu hình tải phân đoạn đa luồng (8 fragments cùng lúc), tăng tốc độ tải về gấp 4-8 lần.
- **Báo cáo tiến trình thời gian thực:** Extension cập nhật tiến trình mỗi giây (phần trăm tải, tốc độ, dung lượng, trạng thái chuyển đổi MP3).
- **Hệ thống điều khiển mạnh mẽ:**
  * **Dừng tải (Cancel):** Ngắt lập tức toàn bộ tiến trình đang tải và hủy các bài đang trong hàng đợi.
  * **Tải lại bài lỗi (Retry Failed):** Tự động lọc các bài bị lỗi trong đợt tải trước để thực hiện lại chỉ với 1 click.
  * **Khóa phiên độc lập (`run_id`):** Đảm bảo worker của lượt tải cũ đã hủy không bao giờ ghi đè lên trạng thái của lượt tải mới.

---

## 12. Tự Động Loại Bỏ Đoạn Thừa (SponsorBlock Integration)

- Tích hợp công nghệ **SponsorBlock** chính thức cho nền tảng YouTube.
- Tự động phát hiện và cắt bỏ hoàn toàn các đoạn:
  * `music_offtopic`: Đoạn hội thoại, phỏng vấn hoặc kịch bản không liên quan đến bài nhạc trong MV.
  * `sponsor`: Đoạn quảng cáo, tài trợ nhãn hàng chèn giữa bài.
  * `selfpromo`: Đoạn tự quảng bá kênh, kêu gọi đăng ký.
  * `intro` / `outro`: Đoạn mở đầu / kết thúc thừa.

---

## 13. Cơ Chế Làm Sạch Tên Tệp & Bảo Toàn Cấu Trúc Đĩa

- **Cấu trúc lưu trữ chuẩn:** `[Thư Mục Lưu]/[Tên Nghệ Sĩ]/[Tên Bài Hát].mp3`
- **Xóa dấu tiếng Việt 100%:** Loại bỏ toàn bộ dấu thanh tiếng Việt (ví dụ: `Sơn Tùng M-TP/Âm Thầm Bên Em.mp3` ➔ `Son Tung M-TP/Am Tham Ben Em.mp3`).
- **Khử bỏ ký tự cấm trên Windows:** Tự động loại bỏ các ký tự `\ / : * ? " < > |`.
- **Cơ chế chống khóa file (File Lock Retry Engine):** Thử lại đổi tên tệp tối đa 5 lần với độ trễ 100ms, khắc phục triệt để lỗi `WinError 32` (File is being used by another process) trên hệ điều hành Windows.
