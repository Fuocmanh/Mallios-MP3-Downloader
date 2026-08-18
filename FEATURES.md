# Chi tiết tính năng Mallios MP3 Downloader

Tài liệu này mô tả hành vi hiện tại của luồng tải và các tính năng chính trong mã nguồn.

## 1. Tải và chuyển đổi audio

Mallios nhận URL đơn lẻ hoặc danh sách URL/playlist, dùng yt-dlp để lấy audio và FFmpeg để chuyển đổi sang MP3. Tùy chọn chất lượng, metadata, thumbnail, loudnorm, tên file và thư mục đích được truyền từ FE xuống backend. Backend hỗ trợ lưu local và luồng lưu Google Drive theo cấu hình của project.

## 2. Theo dõi tiến trình

Backend duy trì hai lớp trạng thái. PROGRESS_STATE phản ánh batch tổng thể; PARALLEL_PROGRESS phản ánh từng bài. FE polling trạng thái định kỳ và khóa request đang chạy để tránh chồng polling. Dữ liệu tiến trình gồm tổng số bài, số bài đã hoàn tất, bài hiện tại, phần trăm, số bài trùng, số bài lỗi và thông báo hiện tại.

Bài trùng được đánh dấu riêng và không tải lại nếu đã có trong lịch sử hoặc file đích. Bài lỗi không bị coi là trùng và vẫn nằm trong danh sách retry.

## 3. Retry và bài lỗi

Luồng yt-dlp có retry hữu hạn cho lỗi extractor, fragment, file access và lỗi tải chung. Cấu hình hiện tại là retries 5 lần, extractor retries 3 lần, fragment retries 5 lần, file access retries 5 lần, socket timeout 10 giây, retry sleep tăng dần và tối đa 4 fragment đồng thời.

Khi retry hết mà bài vẫn lỗi, backend không dừng các worker khác. Bài được ghi với trạng thái failed và thông báo rút gọn. Endpoint /retry-failed lấy lại các URL failed để chạy lại sau khi lỗi tạm thời hết.

> Video đã bị xóa, đặt riêng tư hoặc bị nguồn chặn hoàn toàn không thể được phục hồi bằng retry.

## 4. Preview audio

Preview dùng cache direct stream trong backend. Backend preload tối đa ba URL bằng hai worker; frontend chỉ prefetch bài đầu tiên. Preview bị rate-limit hoặc video không khả dụng trả status=unavailable thay vì HTTP 500, vì preview không được làm hỏng tải local.

## 5. Lưu local và Google Drive

Ở chế độ local, file tạm được đặt trong thư mục tạm của hệ thống và file cuối được ghi vào thư mục đích. Ở chế độ Drive, backend dùng cấu hình Drive hiện có để upload và cập nhật tiến trình. History dùng để nhận diện bài đã tải và tránh tải trùng.

## 6. Dừng và khôi phục

Endpoint /cancel đặt cờ hủy và cố gắng dừng process đang chạy. Batch sau khi hủy phải trả trạng thái rõ ràng, không polling vô hạn. Khi backend restart, trạng thái trong RAM được khởi tạo lại; lịch sử file phụ thuộc dữ liệu trên disk và cấu hình Drive.

## 7. Bảng thông báo

| Thông báo | Ý nghĩa | Hành động |
|---|---|---|
| YouTube đang giới hạn truy cập | Phiên hoặc request bị YouTube rate-limit. | Chờ, giảm preview, kiểm tra cookie và tải lại sau. |
| Video không khả dụng trên YouTube | Video bị xóa, riêng tư hoặc nguồn không cung cấp nội dung. | Kiểm tra URL/quyền truy cập; không retry vô hạn. |
| Không thể tải bài này | Lỗi chưa được phân loại. | Xem logs/error.log và dùng tải lại bài lỗi. |
| Đang chuẩn bị X bài | Backend đang phân tích playlist. | Chờ trạng thái chuyển sang số bài hoàn tất. |
| Đã tải A bài mới, lỗi B bài | Batch kết thúc có kết quả hỗn hợp. | Kiểm tra danh sách lỗi và tải lại bài lỗi. |

## 8. Kiểm thử vận hành

Sau khi sửa mã, chạy kiểm tra cú pháp Python cho backend/app.py và JavaScript cho extension/background.js và extension/content/content.js. Backend cần trả HTTP 200 cho /api/progress với status idle sau restart. Khi thay đổi Extension, phải reload Extension trong Chrome trước khi thử lại.

Nên thử một danh sách nhỏ trước, quan sát total, completed, current và failed, rồi mới tăng số lượng. Không dùng preload nhiều bài để kiểm tra tải vì preview và tải là hai luồng khác nhau.

## 9. Giới hạn

Hệ thống có thể retry lỗi tạm thời nhưng không thể tạo lại nội dung đã bị nguồn xóa hoặc chặn hoàn toàn. Rate-limit của YouTube nằm ngoài quyền kiểm soát của Mallios; ứng dụng chỉ có thể giảm tốc độ, giảm concurrency, chờ giữa các lần thử và ghi nhận bài lỗi để tải lại sau.
