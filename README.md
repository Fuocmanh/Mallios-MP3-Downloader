# Mallios MP3 Downloader

Mallios là Chrome Extension cho Windows, gồm frontend trong extension/ và backend Flask trong backend/app.py. Ứng dụng dùng yt-dlp để tải audio, FFmpeg để chuyển sang MP3 và hỗ trợ lưu local hoặc Google Drive.

## Kiến trúc

| Thành phần | Vai trò |
|---|---|
| extension/content/content.js | Giao diện, chọn bài, gửi yêu cầu tải, polling tiến trình và hiển thị bài lỗi. |
| extension/background.js | Cầu nối request từ Extension đến backend, có timeout và retry. |
| backend/app.py | API Flask, job tải, trạng thái từng bài, retry yt-dlp, lưu file, lịch sử và preview. |
| tools/yt-dlp.exe | Phân tích và tải nội dung từ nguồn được hỗ trợ. |
| FFmpeg | Chuyển audio sang MP3 và xử lý metadata/thumbnail. |
| logs/ | Log khởi động, lỗi và hoạt động tải. |

## Khởi động

Chạy run.bat ở thư mục gốc. Sau khi sửa JavaScript, mở chrome://extensions, bật Developer mode và bấm Reload trên Mallios.

## Luồng tải

FE gửi danh sách URL đến /download. Backend tạo trạng thái riêng cho từng bài trong PARALLEL_PROGRESS và trạng thái tổng trong PROGRESS_STATE. FE gọi /api/progress định kỳ nhưng không tạo polling chồng nhau. Backend gửi sớm total, completed và current để FE hiển thị tiến trình ngay khi đang chuẩn bị playlist.

Mỗi bài có trạng thái, phần trăm, thông báo, chỉ số và cờ trùng lặp. Bài đã có trong lịch sử hoặc thư mục đích được đánh dấu trùng; bài lỗi không bị coi là trùng và vẫn có thể tải lại.

## Retry và chống treo

Luồng yt-dlp sử dụng retry có giới hạn: --retries 5, --extractor-retries 3, --fragment-retries 5, --file-access-retries 5, --retry-sleep exp=1:8, --socket-timeout 10 và --concurrent-fragments 4. Các tham số này xử lý lỗi mạng, extractor, fragment và đọc/ghi file mà không chờ vô hạn.

Nếu một bài vẫn thất bại, backend đánh dấu bài đó là failed, ghi thông báo ngắn gọn và tiếp tục các bài khác. Các bài lỗi được giữ lại để endpoint /retry-failed chạy lại; không bị bỏ âm thầm.

> Không thể tải nội dung đã bị xóa, đặt riêng tư hoặc bị nguồn chặn hoàn toàn. Với lỗi tạm thời, hệ thống retry trong giới hạn; retry vô hạn sẽ làm tiến trình khó kiểm soát và có thể làm rate-limit nặng hơn.

## Preview và rate-limit

Preview là chức năng phụ, không quyết định tải local. Backend preload tối đa ba URL bằng hai worker; FE chỉ prefetch bài đầu tiên. Nếu YouTube rate-limit hoặc video không khả dụng, /api/preview-info và /api/preview-stream trả status=unavailable thay vì HTTP 500. FE hiển thị thông báo ngắn và luồng tải local vẫn tiếp tục.

## API quan trọng

| Endpoint | Phương thức | Chức năng |
|---|---|---|
| /download | POST | Khởi động batch tải. |
| /api/progress | GET | Lấy trạng thái tổng và từng bài. |
| /retry-failed | POST | Tải lại bài có trạng thái failed. |
| /cancel | POST | Dừng batch hiện tại. |
| /api/preview-info | GET/POST | Lấy direct stream URL cho preview. |
| /api/preview-stream | GET | Phát preview qua redirect. |
| /api/preload-playlist | POST | Preload giới hạn các bài đầu tiên. |
| /api/restart | POST | Khởi tạo lại service/job state cục bộ. |

## Xử lý lỗi

Nếu FE không đổi trạng thái, kiểm tra /api/progress, logs/startup.log và logs/error.log, sau đó reload Extension. Nếu log có rate-limited, không tăng worker hoặc preload; hãy chờ giới hạn hết, kiểm tra cookie và dùng tải lại bài lỗi sau. Nếu một bài lỗi nhưng batch vẫn chạy, đó là hành vi thiết kế: lỗi được ghi riêng và không làm dừng các bài khác.

## Lưu ý dữ liệu

Kiểm tra git diff trước khi triển khai. Không đưa cookie YouTube, token Google Drive hoặc file backup chứa thông tin xác thực vào Git.

## Giấy phép

Dự án được phân phối theo giấy phép MIT nếu không có thông báo khác trong repository.
