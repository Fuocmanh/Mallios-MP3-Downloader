# Chi Tiết Tính Năng Mallios MP3 Downloader (v3.4)

Tài liệu này mô tả toàn diện và chi tiết tất cả các tính năng, kiến trúc kỹ thuật và cơ chế vận hành của hệ thống **Mallios MP3 Downloader**.

---

## 1. Giao diện nút nổi thông minh (Floating UI)

- **Đa nền tảng hỗ trợ:** Tự động chèn giao diện tiện ích vào YouTube, YouTube Music, SoundCloud, TikTok, Facebook, Instagram.
- **Kéo thả tùy biến vị trí:** Người dùng có thể kéo thả nút Mallios đến bất kỳ vị trí nào trên màn hình. Tọa độ được ghi nhớ độc lập theo từng tên miền thông qua `localStorage`.
- **Tự động căn chỉnh thông minh:** Khi bấm mở bảng điều khiển, cửa sổ popup sẽ tự động tính toán góc màn hình (trên/dưới/trái/phải) để hiển thị trọn vẹn, không bao giờ bị tràn ra ngoài khung nhìn trình duyệt.
- **3 Tab chức năng chính:**
  1. **Tải nhanh (Quick Download):** Tải ngay video/bài hát đang phát với tùy chọn chất lượng và số lượng bài.
  2. **Chọn bài (Playlist Selector):** Quét danh sách phát, nghe thử trực tiếp và chọn tải từng bài cụ thể.
  3. **Lịch sử (History Manager):** Quản lý bài đã tải, phát lại âm thanh cục bộ, mở thư mục chứa tệp và xem liên kết Google Drive.

---

## 2. Trích xuất Playlist Siêu Tốc (Instant DOM Scraper - 0.001s)

- **Cơ chế đọc trực tiếp từ DOM:** Khi người dùng mở danh sách phát trên YouTube hoặc YouTube Music, tiện ích sẽ đọc trực tiếp dữ liệu bài hát từ bộ nhớ giao diện DOM (`ytd-playlist-panel-video-renderer`, `ytmusic-responsive-list-item-renderer`, `ytd-playlist-video-renderer`).
- **Tốc độ phản hồi tức thì:** Danh sách 10 đến 100+ bài hát hiển thị lên bảng điều khiển chỉ trong **`0.001 giây`** (chớp mắt) mà không cần gửi yêu cầu mạng hay chờ máy chủ phân tích.
- **Cơ chế dự phòng (Server Fallback):** Nếu không đọc được từ DOM (ví dụ URL playlist tổng quát dạng link), hệ thống sẽ tự động gọi API `/get-playlist` phía Flask server để phân tích nhanh danh sách bằng `yt-dlp` flat-playlist.

---

## 3. Nghe Thử Trực Tiếp Siêu Tốc (Direct 302 CDN Streaming)

- **Chuyển hướng trực tiếp Google CDN (HTTP 302 Redirect):**
  * Route API `/api/preview-stream` trích xuất luồng audio trực tiếp từ YouTube (`ba/18/b` android client) và phản hồi mã **`HTTP 302 Redirect`** trực tiếp đến cụm máy chủ Googlevideo CDN tốc độ cao.
  * Trình duyệt kết nối trực tiếp với CDN của Google, giúp phát nhạc với băng thông mạng tối đa và không tiêu tốn RAM của máy tính.
- **Bộ nhớ RAM Cache Stream (`PREVIEW_STREAM_CACHE`):**
  * Lưu trữ đường dẫn stream vào RAM cache trong 30 phút.
  * Khi bấm phát lại bài hát đã nghe, hệ thống phản hồi ngay trong **`0.01 giây` (tức thì)**.
- **Hỗ trợ đầy đủ trình phát HTML5 & Tua nhạc (Seeking):**
  * Hỗ trợ đầy đủ HTTP Range Request 206, giúp người dùng tua đến bất kỳ đoạn nào trong bài hát nghe thử mà không bị ngắt quãng.
- **Khóa chống nghẽn luồng (Thread-safe In-flight Locks):**
  * Tránh tình trạng nhiều yêu cầu cùng trích xuất 1 bài hát, tập trung 100% CPU để phục vụ bài hát người dùng đang nghe.

---

## 4. Cơ Chế Tải Đa Luồng Song Song (Parallel Downloader)

- **Tối đa 5 bài hát đồng thời:** Backend sử dụng `ThreadPoolExecutor` để tải đồng thời tối đa 5 bài hát song song.
- **Đa luồng kết nối cho từng bài (`-N 8`):** Mỗi tiến trình `yt-dlp` được cấu hình tải phân đoạn đa luồng (8 fragments cùng lúc), tăng tốc độ tải về gấp 4-8 lần.
- **Báo cáo tiến trình thời gian thực:** Extension cập nhật tiến trình mỗi giây (phần trăm tải, tốc độ, dung lượng, trạng thái chuyển đổi MP3).
- **Hệ thống điều khiển mạnh mẽ:**
  * **Dừng tải (Cancel):** Ngắt lập tức toàn bộ tiến trình đang tải và hủy các bài đang trong hàng đợi.
  * **Tải lại bài lỗi (Retry Failed):** Tự động lọc các bài bị lỗi trong đợt tải trước để thực hiện lại chỉ với 1 click.
  * **Khóa phiên độc lập (`run_id`):** Đảm bảo worker của lượt tải cũ đã hủy không bao giờ ghi đè lên trạng thái của lượt tải mới.

---

## 5. Tự Động Loại Bỏ Đoạn Thừa (SponsorBlock Integration)

- Tích hợp công nghệ **SponsorBlock** chính thức cho nền tảng YouTube.
- Tự động phát hiện và cắt bỏ hoàn toàn các đoạn:
  * `music_offtopic`: Đoạn hội thoại, phỏng vấn hoặc kịch bản không liên quan đến bài nhạc trong MV.
  * `sponsor`: Đoạn quảng cáo, tài trợ nhãn hàng chèn giữa bài.
  * `selfpromo`: Đoạn tự quảng bá kênh, kêu gọi đăng ký.
  * `intro` & `outro`: Đoạn dạo đầu hoặc kết thúc dài dòng.
- File MP3 tải về là bản nhạc thuần túy, liền mạch và hoàn hảo nhất.

---

## 6. Đồng Bộ Google Drive Tự Động (OAuth 2.0 Integration)

- **Xác thực an toàn:** Tích hợp quy trình Google OAuth 2.0 chuẩn quốc tế (`drive_service.py`).
- **Đăng nhập 1-Click trên Extension:** Người dùng bấm đăng nhập trực tiếp trên giao diện tiện ích để cấp quyền lưu trữ tệp.
- **Tự động tải lên Drive:** Khi kích hoạt chế độ lưu Drive, sau khi chuyển đổi thành MP3, máy chủ sẽ tự động tải file lên thư mục Google Drive cá nhân của bạn và trả về liên kết xem trực tiếp.
- **Bảo mật tuyệt đối:** Mã token (`drive_auth.json`) và thông tin cấu hình (`drive_config.json`) được lưu trữ cục bộ trong thư mục `configs/` và luôn được bảo vệ khỏi Git.

---

## 7. Chuẩn Hóa Tên Tệp & Chống Tải Trùng Lặp Thông Minh

- **Tổ chức thư mục chuẩn:** Tệp nhạc được tự động phân loại theo cấu trúc: `Thư Mục Lưu/Tên Nghệ Sĩ/Tên Bài Hát.mp3`.
- **Làm sạch tên Windows & Bỏ dấu Tiếng Việt:**
  * Loại bỏ các ký tự cấm của Windows (`\`, `/`, `:`, `*`, `?`, `"`, `<`, `>`, `|`).
  * Loại bỏ các cụm từ thừa: `[Official MV]`, `(Lyrics Video)`, `4K`, `1080p`, `Full Audio`, v.v.
  * Chuyển toàn bộ tên tệp và thư mục sang tiếng Việt không dấu chuẩn UTF-8 để tương thích hoàn hảo với mọi đầu phát nhạc trên ô tô, loa Bluetooth, USB.
- **Thuật toán quét trùng lặp trên ổ đĩa:**
  * Trước khi tải, hệ thống quét thư mục lưu và thư mục nghệ sĩ.
  * So khớp thông minh theo tên chuẩn hóa và tiền tố nghệ sĩ (ví dụ: `Son Tung M-TP - Hay Trao Cho Anh.mp3` và `Hay Trao Cho Anh.mp3`).
  * Nếu đã tồn tại file trên đĩa ➔ Đánh dấu hoàn thành 100% với trạng thái **Đã có (Bỏ qua)**, tiết kiệm 100% băng thông và thời gian.

---

## 8. Quản Lý Lịch Sử & Phát Nhạc Cục Bộ (History Manager)

- **Lưu trữ an toàn:** Ghi lịch sử an toàn nguyên tử (Atomic Write) qua file tạm và sao lưu định kỳ vào `configs/history.json`.
- **Các tính năng trên tab Lịch sử:**
  * Phát trực tiếp bài nhạc đã tải với thanh điều khiển tua thời gian và âm lượng.
  * Bấm nút thư mục 📂 để mở Windows Explorer và khoanh vùng tô đậm chính xác file MP3 trên máy tính.
  * Bấm nút mở liên kết 🌐 để truy cập trực tiếp bài nhạc trên Google Drive (nếu lưu Drive).
  * Xóa mục lịch sử, kèm tùy chọn xóa vĩnh viễn file MP3 trên ổ cứng (tự động xóa thư mục nghệ sĩ nếu rỗng).

---

## 9. Bộ Khởi Động & Cài Đặt Tự Động 1-Click (`run.bat` & `install.bat`)

- **Khởi động All-In-One (`run.bat`):**
  * Tự động kiểm tra công cụ `tools/yt-dlp.exe` và `tools/ffmpeg.exe`.
  * Tự động phát hiện môi trường Python (Python nhúng `runtime/`, môi trường ảo `.venv/`, hoặc Python hệ thống).
  * Nếu phát hiện thiếu (ví dụ vừa clone từ GitHub về): **Tự động kích hoạt bộ cài đặt tải đầy đủ công cụ và thư viện cần thiết trong 1 phút**.
  * Tự động bật máy chủ API `127.0.0.1:37491` ngay sau khi sẵn sàng.
- **Native Messaging Host (`com.mallios.mp3`):**
  * Viết bằng C# hiệu năng cao, tự động đăng ký Registry cho Chrome, Edge, Brave, Cốc Cốc.
  * Giúp Extension có thể tự đánh thức và khởi động máy chủ Flask ngầm khi người dùng mở trình duyệt.

---

## 10. Cấu Trúc Thư Mục & Quản Lý Dữ Liệu

- **`configs/`:** Quản lý tập trung toàn bộ file cấu hình JSON và file mẫu `.example.json`.
- **`logs/`:** Lưu trữ toàn bộ nhật ký `error.log` và `startup.log` phục vụ việc chẩn đoán hệ thống.
- **`downloads/`:** Thư mục tải về mặc định.
- **`tools/`:** Chứa các công cụ binary (được bảo vệ bởi `.gitignore` và tự động tải khi cần).
