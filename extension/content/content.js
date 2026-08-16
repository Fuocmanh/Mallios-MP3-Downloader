(function () {
  try {
    const oldRoot = document.getElementById('yt-mp3-root');
    if (oldRoot) oldRoot.remove();

    const SVG = {
      music: `<svg viewBox="0 0 24 24"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>`,
      eq: `<svg viewBox="0 0 24 24"><path d="M7 18h2V6H7v12zm4 4h2V2h-2v20zm-8-8h2v-4H3v4zm12 4h2V6h-2v12zm4-8v4h2v-4h-2z"/></svg>`,
      close: `<svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>`,
      bolt: `<svg viewBox="0 0 24 24"><path d="M11 21h-1l1-7H7.5c-.58 0-.57-.32-.38-.66.19-.34.05-.08.07-.12C8.48 10.94 10.42 7.54 13 3h1l-1 7h3.5c.49 0 .56.33.47.51l-.07.15C14.4 14.55 12.3 18.15 11 21z"/></svg>`,
      library: `<svg viewBox="0 0 24 24"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8 12.5v-7l6 3.5-6 3.5z"/></svg>`,
      gear: `<svg viewBox="0 0 24 24"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>`,
      minus: `<svg viewBox="0 0 24 24"><path d="M19 13H5v-2h14v2z"/></svg>`,
      plus: `<svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>`,
      download: `<svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>`,
      search: `<svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>`,
      check: `<svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>`,
      folder: `<svg viewBox="0 0 24 24"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>`,
      drive: `<svg viewBox="0 0 24 24"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95C8.08 7.14 9.94 6 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11c1.56.1 2.78 1.41 2.78 2.96 0 1.65-1.35 3-3 3z"/></svg>`
    };

    const container = document.createElement('div');
    container.id = 'yt-mp3-root';
    container.innerHTML = `
      <div id="yt-mp3-bubble" title="Bấm để mở MP3 Downloader">
        ${SVG.music}
      </div>

      <div id="yt-mp3-window">
        <div class="yt-mp3-header">
          <div class="yt-mp3-title">
            ${SVG.eq}
            <span>Mallios MP3</span>
            <span id="yt-server-status-badge" class="yt-status-badge offline" title="Bấm để kiểm tra / kết nối máy chủ">🔴 Offline</span>
          </div>
          <button class="yt-mp3-close" id="yt-mp3-close-btn">${SVG.close}</button>
        </div>

        <div class="yt-mp3-tabs">
          <button class="yt-mp3-tab-btn active" id="yt-tab-quick-btn">${SVG.bolt} Tải Nhanh</button>
          <button class="yt-mp3-tab-btn" id="yt-tab-select-btn">${SVG.library} Chọn Bài</button>
          <button class="yt-mp3-tab-btn" id="yt-tab-history-btn">${SVG.music} Lịch sử</button>
          <button class="yt-mp3-tab-btn" id="yt-tab-settings-btn">${SVG.gear} Cài Đặt</button>
        </div>

        <!-- TAB 1: TẢI NHANH -->
        <div class="yt-mp3-content active" id="yt-tab-quick">
          <div class="yt-quick-info-box" style="background: #1e1f25; border-radius: 12px; padding: 12px 14px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.05); font-size: 11px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #8e9099;">Nơi lưu trữ:</span>
              <span id="yt-quick-target-badge" style="color: #a8c7fa; font-weight: 600;">💻 Máy tính</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #8e9099;">Chất lượng:</span>
              <span id="yt-quick-quality-badge" style="color: #c2efb3; font-weight: 600;">320 kbps (Cực cao)</span>
            </div>
          </div>
          <button class="yt-mp3-btn yt-mp3-btn-primary" id="yt-btn-quick-download">
            ${SVG.download} TẢI NGAY MP3
          </button>
        </div>

        <!-- TAB 2: CHỌN BÀI -->
        <div class="yt-mp3-content" id="yt-tab-select">
          <button class="yt-mp3-btn yt-mp3-btn-accent" id="yt-btn-scan">${SVG.search} Quét danh sách bài hát</button>
          
          <!-- Thanh Nghe Thử Trực Tiếp (Preview Player Bar) -->
          <div id="yt-preview-player-bar" class="yt-preview-player-bar" style="display: none;">
            <div class="yt-preview-header">
              <div class="yt-preview-title-box">
                <span class="yt-preview-anim-disc">🎵</span>
                <span id="yt-preview-title" class="yt-preview-title">Đang phát bài hát...</span>
              </div>
              <div style="display: flex; align-items: center; gap: 4px; flex: 0 0 auto;">
                <div class="yt-volume-box">
                  <button type="button" id="yt-preview-vol-btn" class="yt-volume-btn" title="Bật / Tắt tiếng">🔊</button>
                  <input type="range" id="yt-preview-vol-slider" class="yt-volume-slider" min="0" max="1" step="0.05" value="1" title="Âm lượng">
                </div>
                <button type="button" id="yt-preview-autoplay-btn" class="yt-preview-autoplay-btn active" title="Tự động phát bài tiếp theo (Đang Bật)">
                  🔁 Tự phát
                </button>
                <button type="button" id="yt-preview-close-btn" class="yt-preview-close-btn" title="Đóng nghe thử">✕</button>
              </div>
            </div>
            <div class="yt-preview-controls">
              <button type="button" id="yt-preview-prev-btn" class="yt-preview-nav-btn" title="Bài trước (⏮) hoặc Phím P">⏮</button>
              <button type="button" id="yt-preview-toggle-btn" class="yt-preview-toggle-btn" title="Phát / Tạm dừng (Space)">▶</button>
              <button type="button" id="yt-preview-next-btn" class="yt-preview-nav-btn" title="Bài tiếp theo (⏭) hoặc Phím N">⏭</button>
              <span id="yt-preview-current-time" class="yt-preview-time">00:00</span>
              <input type="range" id="yt-preview-seek-bar" class="yt-preview-seek-bar" min="0" max="100" value="0" step="0.1">
              <span id="yt-preview-total-time" class="yt-preview-time">00:00</span>
            </div>
            <audio id="yt-preview-audio-element" style="display: none;"></audio>
          </div>

          <!-- Ô Lọc & Tìm Kiếm Playlist -->
          <div class="yt-search-filter-box" id="yt-search-filter-box" style="display: none;">
            <span style="font-size: 11px; color: #8e9099;">🔍</span>
            <input type="text" id="yt-playlist-search-input" class="yt-search-filter-input" placeholder="Lọc bài hát theo tên hoặc nghệ sĩ...">
            <button type="button" id="yt-playlist-search-clear" style="background: transparent; border: none; color: #8e9099; cursor: pointer; font-size: 10px; padding: 0;" title="Xóa tìm kiếm">✕</button>
          </div>

          <div id="yt-list-section">
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #8e9099;">
              <span>Danh sách bài:</span>
              <span id="yt-select-all" style="color: #a8c7fa; cursor: pointer;">Chọn tất cả</span>
            </div>
            <div class="yt-mp3-list" id="yt-list-container"></div>
            <button class="yt-mp3-btn yt-mp3-btn-success" id="yt-btn-download-selected">
              ${SVG.check} Tải đã chọn ( <span id="yt-select-count">0</span> )
            </button>
          </div>
        </div>
   
        <!-- TAB 3: LỊCH SỬ -->
        <div class="yt-mp3-content" id="yt-tab-history">
          <!-- Toolbar Lịch sử & Nút Đồng bộ -->
          <div class="yt-history-toolbar">
            <div style="font-size: 11px; color: #8e9099; display: flex; align-items: center; gap: 4px;">
              <span>Tổng cộng:</span>
              <b id="yt-history-total-count" style="color: #a8c7fa;">0 bài</b>
            </div>
            <button type="button" id="yt-btn-sync-history" class="yt-history-sync-btn" title="Quét lại toàn bộ file tải trên máy & Drive để đồng bộ chính xác">
              🔄 Đồng bộ
            </button>
          </div>

          <!-- Thanh Trình Phát Lịch Sử (History Player Bar với tua nhạc) -->
          <div id="yt-history-player" class="yt-preview-player-bar" style="display: none; margin-top: 0; margin-bottom: 6px;">
            <div class="yt-preview-header">
              <div class="yt-preview-title-box">
                <span class="yt-preview-anim-disc">🎧</span>
                <span id="yt-player-title" class="yt-preview-title">Tên bài hát</span>
              </div>
              <div style="display: flex; align-items: center; gap: 4px;">
                <button type="button" id="yt-history-autoplay-btn" class="yt-preview-autoplay-btn active" title="Tự động phát bài tiếp trong Lịch sử">
                  🔁 Tự phát
                </button>
                <button type="button" id="yt-player-close-btn" class="yt-preview-close-btn" title="Đóng trình phát">✕</button>
              </div>
            </div>
            <div id="yt-history-audio-controls" class="yt-preview-controls">
              <button type="button" id="yt-history-prev-btn" class="yt-preview-nav-btn" title="Bài trước (⏮)">⏮</button>
              <button type="button" id="yt-player-play-btn" class="yt-preview-toggle-btn" title="Phát / Tạm dừng">▶</button>
              <button type="button" id="yt-history-next-btn" class="yt-preview-nav-btn" title="Bài tiếp theo (⏭)">⏭</button>
              <span id="yt-player-current-time" class="yt-preview-time">00:00</span>
              <input type="range" id="yt-player-seek-bar" class="yt-preview-seek-bar" min="0" max="100" value="0" step="0.1">
              <span id="yt-player-total-time" class="yt-preview-time">00:00</span>
            </div>
            <audio id="yt-audio-element" style="display: none;"></audio>
          </div>

          <div class="yt-mp3-list" id="yt-history-list" style="display: flex; flex-direction: column; gap: 6px; padding-right: 4px;">
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #8e9099; text-align: center; font-size: 11px;">Chưa có lịch sử tải nhạc.</div>
          </div>
        </div>

        <!-- TAB 4: CÀI ĐẶT -->
        <div class="yt-mp3-content" id="yt-tab-settings">
          <div class="yt-mp3-card" style="flex-direction: column; gap: 8px; align-items: stretch; margin-bottom: 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #8e9099; font-size: 12px; font-weight: 500;">Nơi lưu trữ:</span>
              <div class="yt-storage-toggle">
                <button type="button" class="yt-storage-btn active" id="yt-storage-local-btn" title="Lưu vào máy tính">💻 Máy tính</button>
                <button type="button" class="yt-storage-btn" id="yt-storage-drive-btn" title="Lưu vào Google Drive">☁️ Drive</button>
              </div>
            </div>

            <!-- LOCAL STORAGE BOX -->
            <div id="yt-local-storage-box">
              <div class="yt-path-box">
                <input type="text" id="yt-path-input" placeholder="D:\\Music\\NhacTuyenChon...">
                <button id="yt-btn-browse" type="button">
                  ${SVG.folder} Chọn
                </button>
              </div>
            </div>

            <!-- GOOGLE DRIVE BOX -->
            <div id="yt-drive-storage-box" style="display: none;">
              <div id="yt-drive-not-connected" class="yt-drive-box">
                <div style="display: flex; flex-direction: column; gap: 6px; width: 100%;">
                  <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="color: #c4c6d0; font-size: 11px; font-weight: 500;">Google Apps Script URL:</span>
                    <button type="button" id="yt-btn-drive-guide" style="background: transparent; border: none; color: #a8c7fa; font-size: 10px; cursor: pointer; text-decoration: underline; padding: 0;">
                      📖 Hướng dẫn & Mã
                    </button>
                  </div>
                  <div style="display: flex; gap: 4px; align-items: center;">
                    <input type="text" id="yt-drive-input-script-url" placeholder="https://script.google.com/macros/s/.../exec" style="background: #282930; border: 1px solid #3c3d45; color: #e2e2e9; padding: 5px 8px; border-radius: 6px; font-size: 10px; flex: 1; min-width: 0; box-sizing: border-box;">
                    <button type="button" id="yt-btn-drive-connect" class="yt-drive-connect-btn">
                      🔗 Kết nối
                    </button>
                  </div>
                </div>
              </div>

              <!-- APPS SCRIPT GUIDE & CODE MODAL -->
              <div id="yt-drive-guide-box" class="yt-drive-box" style="display: none; gap: 6px;">
                <div style="font-size: 11px; font-weight: bold; color: #a8c7fa; display: flex; justify-content: space-between; align-items: center;">
                  <span>Cách tạo link Google Drive (30 giây)</span>
                  <a href="https://script.google.com/home/start" target="_blank" style="color: #a8c7fa; font-size: 10px; text-decoration: underline;">Mở script.google.com ↗</a>
                </div>
                <div style="font-size: 9px; color: #c4c6d0; line-height: 1.4;">
                  1. Mở <b>script.google.com</b> ➔ Bấm <b>Dự án mới</b>.<br>
                  2. Dán mã bên dưới ➔ Bấm <b>Triển khai</b> ➔ <b>Tùy chọn triển khai mới</b>.<br>
                  3. Chọn: <b>Ứng dụng web</b> ➔ Quyền truy cập: <b>Bất kỳ ai</b> ➔ Bấm <b>Triển khai</b>.<br>
                  4. Sao chép <b>URL ứng dụng web</b> và dán vào ô trên.
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
                  <button type="button" id="yt-btn-copy-script-code" style="background: #282930; border: 1px solid #3c3d45; color: #c2efb3; padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; cursor: pointer;">
                    📋 Sao chép mã Google Script
                  </button>
                  <button type="button" id="yt-btn-close-guide" style="background: transparent; border: 1px solid #3c3d45; color: #8e9099; padding: 4px 8px; border-radius: 4px; font-size: 10px; cursor: pointer;">
                    Đóng
                  </button>
                </div>
              </div>
              
              <div id="yt-drive-connected" class="yt-drive-box" style="display: none;">
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; width: 100%;">
                  <div style="display: flex; align-items: center; gap: 6px; min-width: 0; flex: 1;">
                    <span style="color: #c2efb3; font-size: 12px;">✅</span>
                    <span id="yt-drive-email" style="color: #a8c7fa; font-size: 11px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Google Drive Webhook</span>
                  </div>
                  <button type="button" id="yt-btn-drive-logout" class="yt-drive-logout-btn" title="Đổi URL hoặc Ngắt kết nối">
                    Đổi URL
                  </button>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px; padding-top: 4px; border-top: 1px dashed rgba(255,255,255,0.08); font-size: 10px; color: #8e9099;">
                  <span>Thư mục Drive:</span>
                  <span id="yt-drive-folder-name" style="color: #e2e2e9; font-weight: bold;">Mallios Music</span>
                </div>
              </div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
              <span style="color: #8e9099; font-size: 12px;">Chất lượng nhạc:</span>
              <select id="yt-quality-select" style="background: #282930; color: #a8c7fa; border: none; padding: 4px 8px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px;">
                <option value="0">320 kbps (Cực cao)</option>
                <option value="2">256 kbps (Thường)</option>
                <option value="5">128 kbps (Tiết kiệm)</option>
              </select>
            </div>

            <!-- TÙY CHỌN ÂM THANH & NÂNG CAO -->
            <div class="yt-advanced-options-box">
              <label class="yt-checkbox-label" title="Lưu trực tiếp file MP3 vào thư mục chỉ định mà không tạo thư mục con theo tên ca sĩ / kênh">
                <input type="checkbox" id="yt-opt-no-subfolder">
                <span>📁 Lưu thẳng vào thư mục (Không tạo thư mục con)</span>
              </label>
              <label class="yt-checkbox-label" title="Tự động cân bằng mức âm lượng giữa các bài theo chuẩn EBU R128 (Tốn thêm 2-3s CPU)">
                <input type="checkbox" id="yt-opt-loudnorm">
                <span>🎚️ Chuẩn hóa âm lượng (Loudnorm)</span>
              </label>
              <label class="yt-checkbox-label" title="Tự động cắt các đoạn quảng cáo, intro tài trợ do tác giả lồng vào video (SponsorBlock)">
                <input type="checkbox" id="yt-opt-sponsorblock">
                <span>🛑 Cắt intro / tài trợ (SponsorBlock)</span>
              </label>
              <label class="yt-checkbox-label" title="Nhúng ảnh bìa chất lượng cao vào bên trong file MP3">
                <input type="checkbox" id="yt-opt-thumbnail">
                <span>🖼️ Nhúng ảnh bìa vào MP3</span>
              </label>
              <label class="yt-checkbox-label" title="Tối ưu tốc độ tải cực hạn bằng cách bỏ qua bước chèn thẻ metadata ID3">
                <input type="checkbox" id="yt-opt-fast-mode">
                <span>⚡ Tải siêu tốc (Bỏ qua Metadata ID3)</span>
              </label>
            </div>
          </div>
        </div>

        <div id="yt-mp3-status"></div>
        <div id="yt-duplicate-box" class="yt-duplicate-box" style="display: none;">
          <div id="yt-duplicate-title" class="yt-duplicate-title">Danh sách trùng</div>
          <div id="yt-duplicate-list" class="yt-duplicate-list"></div>
        </div>
        
        <div id="yt-download-ctrl-box" style="display: none; justify-content: center; gap: 8px; margin-top: 8px; align-items: center;">
          <button class="yt-mp3-btn yt-mp3-btn-accent" id="yt-btn-retry-failed" style="width: auto; padding: 6px 12px; font-size: 11px; margin: 0; border-radius: 12px; display: none;">
            🔄 Tải lại bài lỗi
          </button>
          <button class="yt-mp3-btn" id="yt-btn-cancel-download" style="width: auto; padding: 6px 12px; font-size: 11px; margin: 0; border-radius: 12px; background: #ffb4ab !important; color: #690005 !important; font-weight: bold;">
            🛑 Ngừng tải
          </button>
        </div>

        <div id="yt-mp3-resize-handle" style="position:absolute; right:0; bottom:0; width:18px; height:18px; cursor:se-resize; background:transparent; z-index:10000000; display:flex; align-items:flex-end; justify-content:flex-end; padding:0; box-sizing:border-box;">
          <svg width="10" height="10" viewBox="0 0 8 8" style="color: #8e9099; opacity: 0.8; fill: none; stroke: currentColor; stroke-width: 1.5; pointer-events: none;">
            <line x1="6" y1="2" x2="2" y2="6" />
            <line x1="6" y1="4" x2="4" y2="6" />
          </svg>
        </div>
      </div>
    `;
    document.body.appendChild(container);

    const bubble = document.getElementById('yt-mp3-bubble');
    const win = document.getElementById('yt-mp3-window');
    const closeBtn = document.getElementById('yt-mp3-close-btn');
    const pathInput = document.getElementById('yt-path-input');
    const browseBtn = document.getElementById('yt-btn-browse');

    const tabQuickBtn = document.getElementById('yt-tab-quick-btn');
    const tabSelectBtn = document.getElementById('yt-tab-select-btn');
    const tabHistoryBtn = document.getElementById('yt-tab-history-btn');
    const tabSettingsBtn = document.getElementById('yt-tab-settings-btn');
    const tabQuick = document.getElementById('yt-tab-quick');
    const tabSelect = document.getElementById('yt-tab-select');
    const tabHistory = document.getElementById('yt-tab-history');
    const tabSettings = document.getElementById('yt-tab-settings');

    const optNoSubfolder = document.getElementById('yt-opt-no-subfolder');
    const optLoudnorm = document.getElementById('yt-opt-loudnorm');
    const optSponsorBlock = document.getElementById('yt-opt-sponsorblock');
    const optThumbnail = document.getElementById('yt-opt-thumbnail');
    const optFastMode = document.getElementById('yt-opt-fast-mode');
    const qualitySelect = document.getElementById('yt-quality-select');
    let currentStorageTarget = localStorage.getItem('yt_mp3_storage_target') || 'local';

    function updateQuickBadges() {
      const targetBadge = document.getElementById('yt-quick-target-badge');
      const qualityBadge = document.getElementById('yt-quick-quality-badge');
      if (targetBadge) {
        targetBadge.innerText = currentStorageTarget === 'drive' ? '☁️ Google Drive' : '💻 Máy tính';
      }
      if (qualityBadge && qualitySelect) {
        const qText = qualitySelect.options[qualitySelect.selectedIndex]?.text || '320 kbps (Cực cao)';
        qualityBadge.innerText = qText;
      }
    }

    function syncSettingsToStorage() {
      const settings = {
        yt_mp3_storage_target: currentStorageTarget,
        yt_mp3_save_path: pathInput ? pathInput.value.trim() : '',
        yt_mp3_quality: qualitySelect ? qualitySelect.value : '0',
        yt_opt_no_subfolder: optNoSubfolder ? optNoSubfolder.checked : false,
        yt_opt_loudnorm: optLoudnorm ? optLoudnorm.checked : false,
        yt_opt_sponsorblock: optSponsorBlock ? optSponsorBlock.checked : false,
        yt_opt_thumbnail: optThumbnail ? optThumbnail.checked : false,
        yt_opt_fast_mode: optFastMode ? optFastMode.checked : false
      };
      for (const [key, val] of Object.entries(settings)) {
        localStorage.setItem(key, typeof val === 'boolean' ? (val ? 'true' : 'false') : val);
      }
      try {
        if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
          chrome.storage.local.set(settings);
        }
      } catch (_) {}
      updateQuickBadges();
    }

    if (qualitySelect) {
      qualitySelect.value = localStorage.getItem('yt_mp3_quality') || '0';
      qualitySelect.addEventListener('change', () => syncSettingsToStorage());
    }
    if (optNoSubfolder) {
      optNoSubfolder.checked = localStorage.getItem('yt_opt_no_subfolder') === 'true';
      optNoSubfolder.addEventListener('change', () => syncSettingsToStorage());
    }
    if (optLoudnorm) {
      optLoudnorm.checked = localStorage.getItem('yt_opt_loudnorm') === 'true';
      optLoudnorm.addEventListener('change', () => {
        syncSettingsToStorage();
        if (typeof updateLoudnormState === 'function') {
          updateLoudnormState(optLoudnorm.checked);
        }
      });
    }
    if (optSponsorBlock) {
      optSponsorBlock.checked = localStorage.getItem('yt_opt_sponsorblock') === 'true';
      optSponsorBlock.addEventListener('change', () => {
        syncSettingsToStorage();
        if (typeof updateSponsorBlockState === 'function') {
          updateSponsorBlockState(optSponsorBlock.checked);
        }
      });
    }
    if (optThumbnail) {
      optThumbnail.checked = localStorage.getItem('yt_opt_thumbnail') === 'true';
      optThumbnail.addEventListener('change', () => syncSettingsToStorage());
    }
    if (optFastMode) {
      optFastMode.checked = localStorage.getItem('yt_opt_fast_mode') === 'true';
      optFastMode.addEventListener('change', () => syncSettingsToStorage());
    }

    // Tự động đồng bộ các thiết lập lên chrome.storage khi khởi chạy
    syncSettingsToStorage();

    function getDownloadOptions() {
      return {
        no_subfolder: optNoSubfolder ? optNoSubfolder.checked : false,
        enable_loudnorm: optLoudnorm ? optLoudnorm.checked : false,
        enable_sponsorblock: optSponsorBlock ? optSponsorBlock.checked : false,
        embed_thumbnail: optThumbnail ? optThumbnail.checked : false,
        skip_metadata: optFastMode ? optFastMode.checked : false
      };
    }

    let savedWidth = localStorage.getItem('yt-mp3-width');
    let savedHeight = localStorage.getItem('yt-mp3-height');

    if (savedWidth && parseInt(savedWidth) < 420) {
      savedWidth = '420px';
      localStorage.setItem('yt-mp3-width', savedWidth);
    }
    if (savedHeight && parseInt(savedHeight) < 550) {
      savedHeight = '600px';
      localStorage.setItem('yt-mp3-height', savedHeight);
    }

    if (savedWidth) win.style.width = savedWidth;
    if (savedHeight) win.style.height = savedHeight;

    win.dataset.layout = 'quick';

    const resizeHandle = document.getElementById('yt-mp3-resize-handle');
    let isResizing = false;
    let startWidth, startHeight, startX, startY;

    resizeHandle.addEventListener('mousedown', (e) => {
      e.preventDefault();
      e.stopPropagation();

      isResizing = true;

      const rect = win.getBoundingClientRect();
      startWidth = rect.width;
      startHeight = rect.height;
      startX = e.clientX;
      startY = e.clientY;

      document.addEventListener('mousemove', onResize);
      document.addEventListener('mouseup', stopResize);
    });

    function onResize(e) {
      if (!isResizing) return;

      const bubbleRect = bubble.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      const isLeftHalf = bubbleRect.left < viewportWidth / 2;

      let newWidth = isLeftHalf ? startWidth + (e.clientX - startX) : startWidth - (e.clientX - startX);
      const maxWidth = Math.min(1400, viewportWidth - 20);
      newWidth = Math.max(300, Math.min(maxWidth, newWidth));

      let newHeight = startHeight + (e.clientY - startY);

      let minHeight = 200;
      const activeBtn = document.querySelector('.yt-mp3-tab-btn.active');
      const activeTabId = activeBtn ? activeBtn.id : 'yt-tab-quick-btn';

      const isSelectRich = (activeTabId === 'yt-tab-select-btn' && tabSelect && tabSelect.dataset.listReady === 'true');
      const isHistoryRich = (activeTabId === 'yt-tab-history-btn' && tabHistory && tabHistory.dataset.historyReady === 'true');

      if (isSelectRich || isHistoryRich) {
        minHeight = 350;
      }

      const maxHeight = Math.min(1400, viewportHeight * 0.97);
      newHeight = Math.max(minHeight, Math.min(maxHeight, newHeight));

      win.style.width = `${newWidth}px`;
      win.style.height = `${newHeight}px`;

      if (win.classList.contains('active')) {
        updateWindowPosition();
      }
    }

    function stopResize() {
      if (!isResizing) return;
      isResizing = false;

      document.removeEventListener('mousemove', onResize);
      document.removeEventListener('mouseup', stopResize);

      localStorage.setItem('yt-mp3-width', `${Math.round(win.getBoundingClientRect().width)}px`);
      localStorage.setItem('yt-mp3-height', `${Math.round(win.getBoundingClientRect().height)}px`);

      if (win.classList.contains('active')) {
        updateWindowPosition();
      }
    }

    const API_BASE_URL = 'http://127.0.0.1:37491';
    const serverStatusBadge = document.getElementById('yt-server-status-badge');

    function updateServerStatusBadge(isOnline) {
      if (!serverStatusBadge) return;
      if (isOnline) {
        serverStatusBadge.className = 'yt-status-badge online';
        serverStatusBadge.innerText = '🟢 Sẵn sàng';
        serverStatusBadge.title = 'Máy chủ Mallios đang hoạt động tốt (127.0.0.1:37491)';
      } else {
        serverStatusBadge.className = 'yt-status-badge offline';
        serverStatusBadge.innerText = '🔴 Offline (Mở run.bat)';
        serverStatusBadge.title = 'Máy chủ chưa bật. Bấm vào đây hoặc mở tệp run.bat trong thư mục Mallios!';
      }
    }

    async function checkServerHealth() {
      try {
        const res = await chrome.runtime.sendMessage({ type: 'check-health' });
        updateServerStatusBadge(res && res.online);
      } catch (_) {
        updateServerStatusBadge(false);
      }
    }

    if (serverStatusBadge) {
      serverStatusBadge.addEventListener('click', async () => {
        serverStatusBadge.innerText = '⏳ Đang kiểm tra...';
        try {
          await chrome.runtime.sendMessage({ type: 'ensure-backend' });
          await new Promise(r => setTimeout(r, 600));
          await checkServerHealth();
        } catch (_) {
          updateServerStatusBadge(false);
        }
      });
    }

    async function apiFetch(path, options = {}) {
      try {
        const response = await chrome.runtime.sendMessage({
          type: 'api-request',
          path: path,
          options: {
            method: options.method || 'GET',
            headers: options.headers || { 'Content-Type': 'application/json' },
            body: options.body
          }
        });

        if (response) {
          let parsed = {};
          try { 
            parsed = typeof response.body === 'string' ? JSON.parse(response.body) : (response.body || {}); 
          } catch (_) { 
            parsed = { message: response.body || response.error }; 
          }
          if (response.status === 200 || response.ok) {
            updateServerStatusBadge(true);
            return { ok: true, status: response.status || 200, json: async () => parsed };
          } else {
            if (response.status === 503) {
              updateServerStatusBadge(false);
            }
            return { ok: false, status: response.status || 500, json: async () => parsed };
          }
        }
      } catch (bgError) {
        console.warn('Khong the goi background, thu fetch truc tiep:', bgError);
      }

      try {
        const directRes = await fetch(`${API_BASE_URL}${path}`, options);
        updateServerStatusBadge(true);
        return directRes;
      } catch (firstError) {
        updateServerStatusBadge(false);
        return {
          ok: false,
          status: 503,
          json: async () => ({ 
            status: 'error', 
            message: 'Máy chủ Mallios chưa bật. Vui lòng mở file run.bat trong thư mục Mallios.' 
          })
        };
      }
    }

    pathInput.value = localStorage.getItem('yt_mp3_save_path') || '';
    pathInput.addEventListener('change', () => {
      syncSettingsToStorage();
    });
    pathInput.addEventListener('input', () => {
      syncSettingsToStorage();
    });

    browseBtn.addEventListener('click', async () => {
      showStatus('⏳ Đang mở cửa sổ chọn thư mục...', '#a8c7fa');
      try {
        const res = await apiFetch('/select-folder', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success' && data.path) {
          pathInput.value = data.path;
          syncSettingsToStorage();
          showStatus(`✅ Đã chọn: ${data.path}`, '#c2efb3');
        } else {
          showStatus('', '');
        }
      } catch (e) {
        showStatus('❌ Không thể mở cửa sổ chọn thư mục!', '#f2b8b5');
      }
    });

    // --- GOOGLE DRIVE & STORAGE MODE SETUP ---
    const storageLocalBtn = document.getElementById('yt-storage-local-btn');
    const storageDriveBtn = document.getElementById('yt-storage-drive-btn');
    const localStorageBox = document.getElementById('yt-local-storage-box');
    const driveStorageBox = document.getElementById('yt-drive-storage-box');
    const driveNotConnected = document.getElementById('yt-drive-not-connected');
    const driveConnected = document.getElementById('yt-drive-connected');
    const driveGuideBox = document.getElementById('yt-drive-guide-box');
    const driveInputScriptUrl = document.getElementById('yt-drive-input-script-url');
    const driveGuideBtn = document.getElementById('yt-btn-drive-guide');
    const driveCloseGuideBtn = document.getElementById('yt-btn-close-guide');
    const driveCopyCodeBtn = document.getElementById('yt-btn-copy-script-code');
    const driveEmailSpan = document.getElementById('yt-drive-email');
    const driveFolderSpan = document.getElementById('yt-drive-folder-name');
    const driveConnectBtn = document.getElementById('yt-btn-drive-connect');
    const driveLogoutBtn = document.getElementById('yt-btn-drive-logout');

    const GOOGLE_APPS_SCRIPT_CODE = `function doPost(e) {
  var lock = LockService.getUserLock();
  lock.waitLock(30000);
  try {
    var data = JSON.parse(e.postData.contents);
    if (data.action === "list") {
      return getFileListOutput();
    }
    var filename = data.filename || "song.mp3";
    var artist = data.artist || "Mallios";
    var base64Data = data.base64;
    
    var rootFolder = DriveApp.getRootFolder();
    var rootFolders = rootFolder.getFoldersByName("Mallios Music");
    var malliosFolder = rootFolders.hasNext() ? rootFolders.next() : rootFolder.createFolder("Mallios Music");
    
    var targetFolder = malliosFolder;
    if (artist && artist !== "Mallios") {
      var artistFolders = malliosFolder.getFoldersByName(artist);
      targetFolder = artistFolders.hasNext() ? artistFolders.next() : malliosFolder.createFolder(artist);
    }
    
    var existingFiles = targetFolder.getFilesByName(filename);
    if (existingFiles.hasNext()) {
      var existingFile = existingFiles.next();
      return ContentService.createTextOutput(JSON.stringify({
        status: "success",
        is_duplicate: true,
        file_id: existingFile.getId(),
        url: existingFile.getUrl(),
        view_url: existingFile.getUrl(),
        name: existingFile.getName(),
        message: "Tệp đã tồn tại trên Google Drive (Bỏ qua)."
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    var decoded = Utilities.base64Decode(base64Data);
    var blob = Utilities.newBlob(decoded, "audio/mpeg", filename);
    var file = targetFolder.createFile(blob);
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      is_duplicate: false,
      file_id: file.getId(),
      url: file.getUrl(),
      view_url: file.getUrl(),
      name: file.getName()
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

function doGet(e) {
  var action = (e && e.parameter && e.parameter.action) || "ping";
  if (action === "list") {
    return getFileListOutput();
  }
  return ContentService.createTextOutput(JSON.stringify({
    status: "success",
    message: "Mallios Google Drive Apps Script is ready!"
  })).setMimeType(ContentService.MimeType.JSON);
}

function getFileListOutput() {
  try {
    var rootFolder = DriveApp.getRootFolder();
    var rootFolders = rootFolder.getFoldersByName("Mallios Music");
    if (!rootFolders.hasNext()) {
      return ContentService.createTextOutput(JSON.stringify({ status: "success", files: [] })).setMimeType(ContentService.MimeType.JSON);
    }
    var malliosFolder = rootFolders.next();
    var result = [];
    
    var rootFiles = malliosFolder.getFilesByType("audio/mpeg");
    while (rootFiles.hasNext()) {
      var f = rootFiles.next();
      if (!f.isTrashed()) {
        result.push({
          id: f.getId(),
          name: f.getName(),
          artist: "Mallios",
          url: f.getUrl(),
          size: f.getSize(),
          updated: f.getLastUpdated().getTime()
        });
      }
    }
    
    var subFolders = malliosFolder.getFolders();
    while (subFolders.hasNext()) {
      var subF = subFolders.next();
      if (!subF.isTrashed()) {
        var artistName = subF.getName();
        var subFiles = subF.getFilesByType("audio/mpeg");
        while (subFiles.hasNext()) {
          var sf = subFiles.next();
          if (!sf.isTrashed()) {
            result.push({
              id: sf.getId(),
              name: sf.getName(),
              artist: artistName,
              url: sf.getUrl(),
              size: sf.getSize(),
              updated: sf.getLastUpdated().getTime()
            });
          }
        }
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      files: result
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}`;

    let isDriveConnected = false;

    function applyStorageTarget(target) {
      currentStorageTarget = target;
      syncSettingsToStorage();
      if (target === 'drive') {
        if (storageDriveBtn) storageDriveBtn.classList.add('active');
        if (storageLocalBtn) storageLocalBtn.classList.remove('active');
        if (localStorageBox) localStorageBox.style.display = 'none';
        if (driveStorageBox) driveStorageBox.style.display = 'block';
        checkDriveStatus();
      } else {
        if (storageLocalBtn) storageLocalBtn.classList.add('active');
        if (storageDriveBtn) storageDriveBtn.classList.remove('active');
        if (localStorageBox) localStorageBox.style.display = 'block';
        if (driveStorageBox) driveStorageBox.style.display = 'none';
      }
    }

    if (storageLocalBtn) storageLocalBtn.addEventListener('click', () => applyStorageTarget('local'));
    if (storageDriveBtn) storageDriveBtn.addEventListener('click', () => applyStorageTarget('drive'));

    async function checkDriveStatus() {
      try {
        const res = await apiFetch('/auth/google/status');
        const data = await res.json();
        if (data.status === 'success' && data.data) {
          isDriveConnected = !!data.data.connected;
          
          if (driveInputScriptUrl && data.data.script_url && !driveInputScriptUrl.value) {
            driveInputScriptUrl.value = data.data.script_url;
          }

          if (isDriveConnected) {
            if (driveNotConnected) driveNotConnected.style.display = 'none';
            if (driveGuideBox) driveGuideBox.style.display = 'none';
            if (driveConnected) driveConnected.style.display = 'block';
            if (driveEmailSpan) driveEmailSpan.innerText = data.data.email || 'Google Drive (Apps Script)';
            if (driveFolderSpan) driveFolderSpan.innerText = data.data.folder_name || 'Mallios Music';
          } else {
            if (driveConnected) driveConnected.style.display = 'none';
            if (!driveGuideBox || driveGuideBox.style.display === 'none') {
              if (driveNotConnected) driveNotConnected.style.display = 'block';
            }
          }
        }
      } catch (_) {}
    }

    if (driveGuideBtn) {
      driveGuideBtn.addEventListener('click', () => {
        if (driveGuideBox) driveGuideBox.style.display = 'flex';
      });
    }

    if (driveCloseGuideBtn) {
      driveCloseGuideBtn.addEventListener('click', () => {
        if (driveGuideBox) driveGuideBox.style.display = 'none';
      });
    }

    if (driveCopyCodeBtn) {
      driveCopyCodeBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(GOOGLE_APPS_SCRIPT_CODE);
          const orig = driveCopyCodeBtn.innerText;
          driveCopyCodeBtn.innerText = '✅ Đã sao chép mã!';
          setTimeout(() => { driveCopyCodeBtn.innerText = orig; }, 2500);
        } catch (_) {
          alert('Vui lòng sao chép mã trực tiếp từ hướng dẫn.');
        }
      });
    }

    if (driveConnectBtn) {
      driveConnectBtn.addEventListener('click', async () => {
        const scriptUrl = driveInputScriptUrl ? driveInputScriptUrl.value.trim() : '';
        if (!scriptUrl) {
          showStatus('⚠️ Vui lòng dán Web App URL của Google Apps Script!', '#f2b8b5');
          if (driveGuideBox) driveGuideBox.style.display = 'flex';
          return;
        }

        showStatus('⏳ Đang kiểm tra và kết nối...', '#a8c7fa');
        try {
          const res = await apiFetch('/auth/google/script-url', {
            method: 'POST',
            body: JSON.stringify({ script_url: scriptUrl })
          });
          const data = await res.json();
          if (data.status === 'success') {
            await checkDriveStatus();
            showStatus('✅ Đã kết nối Google Drive thành công!', '#c2efb3');
          } else {
            showStatus(`❌ ${data.message || 'URL không hợp lệ'}`, '#f2b8b5');
          }
        } catch (err) {
          showStatus('❌ Không thể kết nối với máy chủ!', '#f2b8b5');
        }
      });
    }

    if (driveLogoutBtn) {
      driveLogoutBtn.addEventListener('click', async () => {
        const ok = confirm('Bạn có muốn đổi URL hoặc ngắt kết nối Google Drive?');
        if (!ok) return;
        try {
          await apiFetch('/auth/google/logout', { method: 'POST' });
          isDriveConnected = false;
          if (driveInputScriptUrl) driveInputScriptUrl.value = '';
          if (driveNotConnected) driveNotConnected.style.display = 'block';
          if (driveConnected) driveConnected.style.display = 'none';
          if (driveGuideBox) driveGuideBox.style.display = 'none';
          showStatus('✅ Đã ngắt kết nối Google Drive.', '#c2efb3');
        } catch (_) {
          showStatus('❌ Lỗi khi ngắt kết nối!', '#f2b8b5');
        }
      });
    }

    applyStorageTarget(currentStorageTarget);
    checkDriveStatus();
    updateQuickBadges();

    const savedPos = JSON.parse(localStorage.getItem('yt_mp3_bubble_pos') || 'null');
    if (savedPos && typeof savedPos.top === 'number' && typeof savedPos.left === 'number') {
      const safeTop = Math.max(10, Math.min(window.innerHeight - 65, savedPos.top));
      const safeLeft = Math.max(10, Math.min(window.innerWidth - 65, savedPos.left));
      bubble.style.top = safeTop + 'px';
      bubble.style.left = safeLeft + 'px';
    } else {
      bubble.style.top = (window.innerHeight - 80) + 'px';
      bubble.style.left = (window.innerWidth - 80) + 'px';
    }

    checkInitialProgress();

    function updateWindowPosition() {
      const bubbleRect = bubble.getBoundingClientRect();
      const winWidth = win.offsetWidth || 360;
      const winHeight = win.offsetHeight || 380;
      
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      const isTopHalf = bubbleRect.top < viewportHeight / 2;
      const isLeftHalf = bubbleRect.left < viewportWidth / 2;

      let left = isLeftHalf ? bubbleRect.left : bubbleRect.right - winWidth;
      let top = isTopHalf ? bubbleRect.bottom + 12 : bubbleRect.top - winHeight - 12;

      left = Math.max(10, Math.min(viewportWidth - winWidth - 10, left));
      top = Math.max(10, Math.min(viewportHeight - winHeight - 10, top));

      win.style.left = left + 'px';
      win.style.top = top + 'px';

      if (resizeHandle) {
        if (isLeftHalf) {
          resizeHandle.style.left = 'auto'; resizeHandle.style.right = '0'; resizeHandle.style.bottom = '0';
          resizeHandle.style.cursor = 'se-resize'; resizeHandle.style.transform = 'scaleX(1)';
        } else {
          resizeHandle.style.left = '0'; resizeHandle.style.right = 'auto'; resizeHandle.style.bottom = '0';
          resizeHandle.style.cursor = 'sw-resize'; resizeHandle.style.transform = 'scaleX(-1)';
        }
      }
    }

    window.addEventListener('resize', () => {
      const bubbleSize = 52;
      const safeTop = Math.max(10, Math.min(window.innerHeight - bubbleSize - 10, bubble.offsetTop));
      const safeLeft = Math.max(10, Math.min(window.innerWidth - bubbleSize - 10, bubble.offsetLeft));
      bubble.style.top = `${safeTop}px`;
      bubble.style.left = `${safeLeft}px`;

      if (win.classList.contains('active')) {
        updateWindowPosition();
      }
    });

    let isDragging = false, mouseX = 0, mouseY = 0;
    bubble.addEventListener('mousedown', (e) => {
      isDragging = false; mouseX = e.clientX; mouseY = e.clientY;
      const onMouseMove = (e) => {
        isDragging = true;
        const deltaX = mouseX - e.clientX, deltaY = mouseY - e.clientY;
        mouseX = e.clientX; mouseY = e.clientY;
        let newTop = Math.max(10, Math.min(window.innerHeight - 60, bubble.offsetTop - deltaY));
        let newLeft = Math.max(10, Math.min(window.innerWidth - 60, bubble.offsetLeft - deltaX));
        bubble.style.top = newTop + 'px'; bubble.style.left = newLeft + 'px';
        if (win.classList.contains('active')) updateWindowPosition();
      };
      const onMouseUp = () => {
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        if (isDragging) localStorage.setItem('yt_mp3_bubble_pos', JSON.stringify({ top: bubble.offsetTop, left: bubble.offsetLeft }));
      };
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    });

    bubble.addEventListener('click', () => {
      if (!isDragging) {
        if (win.classList.toggle('active')) {
          updateWindowPosition();
          checkServerHealth();
          checkDriveStatus();
        }
      }
    });
    setInterval(() => {
      if (win.classList.contains('active')) {
        checkServerHealth();
      }
    }, 8000);
    closeBtn.addEventListener('click', () => win.classList.remove('active'));

    function deactivateAllTabs() {
      tabQuickBtn.classList.remove('active');
      tabSelectBtn.classList.remove('active');
      tabHistoryBtn.classList.remove('active');
      tabSettingsBtn.classList.remove('active');
      tabQuick.classList.remove('active');
      tabSelect.classList.remove('active');
      tabHistory.classList.remove('active');
      tabSettings.classList.remove('active');
    }

    function applyTabLayout() {
      if (tabQuick.classList.contains('active')) {
        win.dataset.layout = 'quick';
        return;
      }
      if (tabSelect.classList.contains('active')) {
        const ready = tabSelect.dataset.listReady === 'true';
        win.dataset.layout = ready ? 'select-rich' : 'select-empty';
        return;
      }
      if (tabHistory.classList.contains('active')) {
        const ready = tabHistory.dataset.historyReady === 'true';
        win.dataset.layout = ready ? 'history-rich' : 'history-empty';
        return;
      }
      if (tabSettings.classList.contains('active')) {
        win.dataset.layout = 'settings';
        return;
      }
    }

    tabQuickBtn.addEventListener('click', () => {
      deactivateAllTabs();
      tabQuickBtn.classList.add('active');
      tabQuick.classList.add('active');
      applyTabLayout();
      updateWindowPosition();
    });

    tabSelectBtn.addEventListener('click', () => {
      deactivateAllTabs();
      tabSelectBtn.classList.add('active');
      tabSelect.classList.add('active');
      applyTabLayout();
      updateWindowPosition();

      // Tự động quét tức thì từ DOM trang hiện tại nếu danh sách đang trống (< 0.01 giây)
      if (!currentPlaylistItems || currentPlaylistItems.length === 0) {
        const domItems = extractPlaylistFromPageDOM();
        if (domItems && domItems.length > 0) {
          renderList(domItems);
          showStatus(`✅ Đã tìm thấy ${domItems.length} bài trên trang!`, '#c2efb3');
          applyTabLayout();
          updateWindowPosition();
        }
      }
    });

    tabHistoryBtn.addEventListener('click', () => {
      deactivateAllTabs();
      tabHistoryBtn.classList.add('active');
      tabHistory.classList.add('active');
      applyTabLayout();
      updateWindowPosition();
      loadHistoryList();
    });

    tabSettingsBtn.addEventListener('click', () => {
      deactivateAllTabs();
      tabSettingsBtn.classList.add('active');
      tabSettings.classList.add('active');
      applyTabLayout();
      updateWindowPosition();
    });

    // const minusBtn = document.getElementById('yt-minus-btn');
    // const plusBtn = document.getElementById('yt-plus-btn');
    // const maxFiles = document.getElementById('yt-max-files');
    // minusBtn.addEventListener('click', () => { let v = parseInt(maxFiles.innerText) - 1; if (v >= 1) maxFiles.innerText = v; });
    // plusBtn.addEventListener('click', () => { let v = parseInt(maxFiles.innerText) + 1; if (v <= 100) maxFiles.innerText = v; });

    const retryFailedBtn = document.getElementById('yt-btn-retry-failed');
    const cancelDownloadBtn = document.getElementById('yt-btn-cancel-download');

    retryFailedBtn.addEventListener('click', async () => {
      const activeTab = document.querySelector('.yt-mp3-tab-btn.active');
      let activeBtn = document.getElementById('yt-btn-quick-download');
      let origContent = `${SVG.download} TẢI NGAY MP3`;
      if (activeTab && activeTab.id === 'yt-tab-select-btn') {
        activeBtn = document.getElementById('yt-btn-download-selected');
        const countSpan = document.getElementById('yt-select-count');
        const count = countSpan ? countSpan.innerText : '0';
        origContent = `${SVG.check} Tải đã chọn ( <span id="yt-select-count">${count}</span> )`;
      }

      showStatus("⏳ Đang chuẩn bị tải lại các bài lỗi...", "#a8c7fa");
      retryFailedBtn.setAttribute('disabled', 'true');
      retryFailedBtn.innerHTML = "⏳ Đang gửi...";

      try {
        if (currentStorageTarget === 'drive' && !isDriveConnected) {
          showStatus('⚠️ Bạn chưa kết nối Google Drive. Hãy kết nối trước khi tải lại!', '#f2b8b5');
          retryFailedBtn.removeAttribute('disabled');
          retryFailedBtn.innerHTML = "🔄 Tải lại bài lỗi";
          return;
        }

        const response = await apiFetch('/retry-failed', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            quality: document.getElementById('yt-quality-select').value,
            download_path: pathInput.value,
            save_target: currentStorageTarget
          })
        });

        const data = await response.json();
        retryFailedBtn.removeAttribute('disabled');
        retryFailedBtn.innerHTML = "🔄 Tải lại bài lỗi";

        if (data.status === 'success') {
          startProgressPolling(activeBtn, origContent);
        } else {
          showStatus(`❌ ${data.message || 'Không thể tải lại.'}`, '#f2b8b5');
        }
      } catch (_) {
        retryFailedBtn.removeAttribute('disabled');
        retryFailedBtn.innerHTML = "🔄 Tải lại bài lỗi";
        showStatus("❌ Lỗi kết nối khi gửi yêu cầu tải lại!", "#f2b8b5");
      }
    });

    cancelDownloadBtn.addEventListener('click', async () => {
      const confirmStop = confirm("Bạn có chắc chắn muốn ngưng toàn bộ các tiến trình tải đang chạy không?");
      if (!confirmStop) return;

      cancelDownloadBtn.setAttribute('disabled', 'true');
      cancelDownloadBtn.innerHTML = "⏳ Đang ngưng...";

      try {
        const response = await apiFetch('/cancel', { method: 'POST' });
        const data = await response.json();
        cancelDownloadBtn.removeAttribute('disabled');
        cancelDownloadBtn.innerHTML = "🛑 Ngừng tải";

        if (data.status === 'success') {
          showStatus("🛑 Đã ngưng tải tất cả các luồng.", "#f2b8b5");
        } else {
          showStatus(`❌ ${data.message || 'Lỗi khi ngưng tải.'}`, '#f2b8b5');
        }
      } catch (_) {
        cancelDownloadBtn.removeAttribute('disabled');
        cancelDownloadBtn.innerHTML = "🛑 Ngừng tải";
        showStatus("❌ Lỗi kết nối khi gửi yêu cầu ngưng tải!", "#f2b8b5");
      }
    });

    let progressInterval = null;

    function startProgressPolling(btn, originalContent) {
      if (progressInterval) clearInterval(progressInterval);
      
      btn.setAttribute('disabled', 'true');
      bubble.classList.add('loading');
      renderDuplicateList([]);
      
      const ctrlBox = document.getElementById('yt-download-ctrl-box');
      const retryBtn = document.getElementById('yt-btn-retry-failed');
      const cancelBtn = document.getElementById('yt-btn-cancel-download');
      
      if (ctrlBox) {
        ctrlBox.style.display = 'flex';
        cancelBtn.style.display = 'block';
        retryBtn.style.display = 'none';
      }
      
      progressInterval = setInterval(async () => {
        try {
          const res = await apiFetch('/api/progress', { method: 'GET' });
          const data = await res.json();
          
          if (data.status === 'running') {
            showStatus(`⏳ ${data.message}`, '#a8c7fa');
            renderDuplicateList(data.duplicate_files);
            btn.innerHTML = data.percent > 0 ? `⏳ ${data.percent}%` : `⏳ Đang kiểm tra...`;
          } else if (data.status === 'completed') {
            clearInterval(progressInterval);
            progressInterval = null;
            showStatus(`🎉 ${data.message || 'Đã tải thành công vào thư mục!'}`, '#c2efb3');
            renderDuplicateList(data.duplicate_files);
            btn.removeAttribute('disabled');
            bubble.classList.remove('loading');
            btn.innerHTML = originalContent;
            updateCount();
            
            try {
              chrome.runtime.sendMessage({
                type: "show-notification",
                title: "🎉 Mallios MP3",
                message: data.message || "Tất cả bài hát đã được tải về thành công!"
              });
            } catch (_) {}

            if (cancelBtn) cancelBtn.style.display = 'none';
            if (data.has_failed && retryBtn) {
              retryBtn.style.display = 'block';
            } else if (ctrlBox) {
              ctrlBox.style.display = 'none';
            }
          } else if (data.status === 'failed') {
            clearInterval(progressInterval);
            progressInterval = null;
            showStatus(`❌ ${data.error || data.message || 'Tải thất bại.'}`, '#f2b8b5');
            renderDuplicateList(data.duplicate_files);
            btn.removeAttribute('disabled');
            bubble.classList.remove('loading');
            btn.innerHTML = originalContent;
            updateCount();
            
            if (cancelBtn) cancelBtn.style.display = 'none';
            if (data.has_failed && retryBtn) {
              retryBtn.style.display = 'block';
            } else if (ctrlBox) {
              ctrlBox.style.display = 'none';
            }
          } else if (data.status === 'cancelled') {
            clearInterval(progressInterval);
            progressInterval = null;
            showStatus(`🛑 ${data.message || 'Đã ngưng tải.'}`, '#ffb4ab');
            renderDuplicateList(data.duplicate_files);
            btn.removeAttribute('disabled');
            bubble.classList.remove('loading');
            btn.innerHTML = originalContent;
            updateCount();
            
            if (ctrlBox) ctrlBox.style.display = 'none';
          }
        } catch (err) {
          clearInterval(progressInterval);
          progressInterval = null;
          showStatus('❌ Lỗi kết nối kiểm tra tiến trình!', '#f2b8b5');
          btn.removeAttribute('disabled');
          bubble.classList.remove('loading');
          btn.innerHTML = originalContent;
          updateCount();
          if (ctrlBox) ctrlBox.style.display = 'none';
        }
      }, 1000);
    }

    async function checkInitialProgress() {
      try {
        const res = await apiFetch('/api/progress', { method: 'GET' });
        const data = await res.json();
        
        const ctrlBox = document.getElementById('yt-download-ctrl-box');
        const retryBtn = document.getElementById('yt-btn-retry-failed');
        const cancelBtn = document.getElementById('yt-btn-cancel-download');
        
        if (data.status === 'running') {
          const activeTab = document.querySelector('.yt-mp3-tab-btn.active');
          let btn = document.getElementById('yt-btn-quick-download');
          let origContent = `${SVG.download} TẢI NGAY MP3`;
          if (activeTab && activeTab.id === 'yt-tab-select-btn') {
            btn = document.getElementById('yt-btn-download-selected');
            const countSpan = document.getElementById('yt-select-count');
            const count = countSpan ? countSpan.innerText : '0';
            origContent = `${SVG.check} Tải đã chọn ( <span id="yt-select-count">${count}</span> )`;
          }
          startProgressPolling(btn, origContent);
        } else {
          if (data.status === 'cancelled') {
            if (ctrlBox) ctrlBox.style.display = 'none';
          } else if (data.has_failed) {
            if (ctrlBox) ctrlBox.style.display = 'flex';
            if (retryBtn) retryBtn.style.display = 'block';
            if (cancelBtn) cancelBtn.style.display = 'none';
          } else {
            if (ctrlBox) ctrlBox.style.display = 'none';
          }
        }
      } catch (_) {}
    }

    async function performDownload(payload, btn, originalContent) {
      if (progressInterval) {
        showStatus('⚠️ Có tiến trình tải đang chạy. Vui lòng đợi.', '#f2b8b5');
        return;
      }
      
      btn.setAttribute('disabled', 'true');
      btn.innerHTML = `⏳ Đang chuẩn bị tải...`;
      
      bubble.classList.add('loading');
      showStatus("⏳ Đang gửi yêu cầu tải...", "#a8c7fa");

      try {
        const response = await apiFetch('/download', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
          startProgressPolling(btn, originalContent);
        } else {
          showStatus(`❌ ${data.message || 'Lỗi xuất file MP3!'}`, '#f2b8b5');
          btn.removeAttribute('disabled');
          bubble.classList.remove('loading');
          btn.innerHTML = originalContent;
          updateCount();
        }
      } catch (err) {
        showStatus('❌ Lỗi kết nối Server! Hãy kiểm tra cài đặt Native Host.', '#f2b8b5');
        btn.removeAttribute('disabled');
        bubble.classList.remove('loading');
        btn.innerHTML = originalContent;
        updateCount();
      }
    }

    function getTikTokVideoUrl() {
      const items = document.querySelectorAll('[data-e2e="recommend-list-item-container"], [data-e2e="user-post-item-list"] > div');
      let activeUrl = null;
      
      if (items.length > 0) {
        let closestItem = null;
        let minDistance = Infinity;
        const centerY = window.innerHeight / 2;
        
        items.forEach(item => {
          const rect = item.getBoundingClientRect();
          const itemCenter = rect.top + rect.height / 2;
          const distance = Math.abs(centerY - itemCenter);
          if (distance < minDistance) {
            minDistance = distance;
            closestItem = item;
          }
        });
        
        if (closestItem) {
          const links = closestItem.querySelectorAll('a');
          for (let link of links) {
            const href = link.href;
            if (href && href.includes('/video/')) {
              activeUrl = href.split('?')[0];
              break;
            }
          }
        }
      }
      
      if (!activeUrl) {
        const allLinks = document.querySelectorAll('a');
        for (let link of allLinks) {
          const href = link.href;
          if (href && href.includes('/video/')) {
            const rect = link.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.top <= window.innerHeight) {
              activeUrl = href.split('?')[0];
              break;
            }
          }
        }
      }
      
      return activeUrl;
    }

    function getSoundCloudPlayingTrackUrl() {
      const badgeLink = document.querySelector('.playbackSoundBadge__titleLink, a.playbackSoundBadge__titleLink');
      if (badgeLink && badgeLink.href) {
        return badgeLink.href.split('?')[0];
      }
      
      const badge = document.querySelector('.playbackSoundBadge');
      if (badge) {
        const link = badge.querySelector('a');
        if (link && link.href) {
          return link.href.split('?')[0];
        }
      }
      return null;
    }

    function getActiveVideoUrl() {
      const url = window.location.href;
      
      if (url.includes('soundcloud.com')) {
        const isGeneric = ['/discover', '/stream', '/you/', '/charts'].some(path => url.includes(path)) || 
                          url === 'https://soundcloud.com' || url === 'https://soundcloud.com/';
        if (isGeneric) {
          const detected = getSoundCloudPlayingTrackUrl();
          if (detected) return detected;
        }
      }
      
      if (url.includes('tiktok.com')) {
        if (!url.includes('/video/')) {
          const detected = getTikTokVideoUrl();
          if (detected) return detected;
        }
      }
      
      if (url.includes('instagram.com')) {
        if (!url.includes('/p/') && !url.includes('/reel/')) {
          const allLinks = document.querySelectorAll('a');
          for (let link of allLinks) {
            const href = link.href;
            if (href && (href.includes('/p/') || href.includes('/reel/'))) {
              const rect = link.getBoundingClientRect();
              if (rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.top <= window.innerHeight) {
                return href.split('?')[0];
              }
            }
          }
        }
      }
      
      return url;
    }

    // Tải Nhanh (Tab 1)
    document.getElementById('yt-btn-quick-download').addEventListener('click', function () {
      const btn = this;
      const quality = document.getElementById('yt-quality-select').value;
      const savePath = pathInput.value.trim();

      if (currentStorageTarget === 'drive' && !isDriveConnected) {
        showStatus('⚠️ Bạn chưa kết nối Google Drive. Hãy bấm nút Kết nối ở trên!', '#f2b8b5');
        return;
      }

      const originalContent = `${SVG.download} TẢI NGAY MP3`;

      performDownload({
        links: [getActiveVideoUrl()],
        max_files: 1,
        quality: quality,
        download_path: savePath,
        save_target: currentStorageTarget,
        ...getDownloadOptions()
      }, btn, originalContent);
    });

    function extractFromYtInitialData() {
      const items = [];
      const seenIds = new Set();

      function addItem(videoId, title) {
        if (videoId && title && !seenIds.has(videoId)) {
          seenIds.add(videoId);
          items.push({
            id: videoId,
            title: title.trim(),
            url: `https://www.youtube.com/watch?v=${videoId}`
          });
        }
      }

      function parseRenderer(r) {
        if (!r) return;
        const v = r.playlistPanelVideoRenderer || r.playlistVideoRenderer || r.compactVideoRenderer || r.videoRenderer || r.gridVideoRenderer || r.musicResponsiveListItemRenderer;
        if (!v) return;
        const vId = v.videoId;
        let title = '';
        if (v.title) {
          if (typeof v.title.simpleText === 'string') {
            title = v.title.simpleText;
          } else if (Array.isArray(v.title.runs) && v.title.runs.length > 0) {
            title = v.title.runs.map(x => x.text).join('');
          }
        }
        if (!title && v.headline) {
          title = v.headline.simpleText || (v.headline.runs ? v.headline.runs.map(x => x.text).join('') : '');
        }
        if (vId && title) {
          addItem(vId, title);
        }
      }

      function traverseObject(obj, depth = 0) {
        if (!obj || depth > 10 || typeof obj !== 'object') return;
        if (Array.isArray(obj)) {
          for (const it of obj) {
            parseRenderer(it);
            traverseObject(it, depth + 1);
          }
          return;
        }
        if (obj.videoId && (obj.title || obj.headline)) {
          parseRenderer({ videoRenderer: obj });
        }
        for (const k of Object.keys(obj)) {
          if (['playlistPanelVideoRenderer', 'playlistVideoRenderer', 'compactVideoRenderer', 'videoRenderer', 'gridVideoRenderer', 'musicResponsiveListItemRenderer'].includes(k)) {
            parseRenderer(obj);
          } else if (typeof obj[k] === 'object' && obj[k] !== null) {
            traverseObject(obj[k], depth + 1);
          }
        }
      }

      try {
        const scripts = document.querySelectorAll('script');
        for (const s of scripts) {
          const txt = s.textContent || '';
          if (txt.includes('ytInitialData') && (txt.includes('var ytInitialData =') || txt.includes('window["ytInitialData"] =') || txt.includes('ytInitialData ='))) {
            const jsonMatch = txt.match(/ytInitialData\s*=\s*({.+?});/s) || txt.match(/ytInitialData\s*=\s*({.+})/s);
            if (jsonMatch && jsonMatch[1]) {
              try {
                const data = JSON.parse(jsonMatch[1]);
                traverseObject(data);
                if (items.length > 0) return items;
              } catch (_) {}
            }
          }
        }
      } catch (_) {}

      return items;
    }

    function extractPlaylistFromPageDOM() {
      // 1. Ưu tiên trích xuất trực tiếp siêu tốc từ ytInitialData (0.001 giây)
      const ytDataItems = extractFromYtInitialData();
      if (ytDataItems && ytDataItems.length > 0) {
        return ytDataItems;
      }

      const items = [];
      const seenIds = new Set();

      // 2. Panel danh sách phát trên trang xem video (Mix, Radio, Danh sách phát đang nghe, Sidebar)
      const panelItems = document.querySelectorAll('ytd-playlist-panel-video-renderer, ytd-playlist-video-renderer, ytd-compact-video-renderer, ytd-grid-video-renderer, ytd-rich-item-renderer, ytd-video-renderer');
      panelItems.forEach(el => {
        const titleEl = el.querySelector('#video-title, #title, span.ytd-playlist-panel-video-renderer, #video-title-link');
        const linkEl = el.querySelector('a#wc-endpoint, a#video-title, a#thumbnail, a[href*="watch?v="], a[href*="/watch?"]');
        if (titleEl && linkEl) {
          const href = linkEl.getAttribute('href') || '';
          const match = href.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
          const vId = match ? match[1] : '';
          const title = (titleEl.getAttribute('title') || titleEl.textContent || '').trim();
          if (vId && title && !seenIds.has(vId)) {
            seenIds.add(vId);
            items.push({
              id: vId,
              title: title,
              url: `https://www.youtube.com/watch?v=${vId}`
            });
          }
        }
      });

      // 3. Trang danh sách phát YouTube Music
      if (items.length === 0) {
        const ytMusicItems = document.querySelectorAll('ytmusic-responsive-list-item-renderer, ytmusic-player-queue-item');
        ytMusicItems.forEach(el => {
          const titleEl = el.querySelector('.title-column yt-formatted-string, .title a, a[href*="watch?v="], .song-title');
          const linkEl = el.querySelector('a[href*="watch?v="], a[href*="/watch?"]');
          if (titleEl && linkEl) {
            const href = linkEl.getAttribute('href') || '';
            const match = href.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
            const vId = match ? match[1] : '';
            const title = (titleEl.getAttribute('title') || titleEl.textContent || '').trim();
            if (vId && title && !seenIds.has(vId)) {
              seenIds.add(vId);
              items.push({
                id: vId,
                title: title,
                url: `https://www.youtube.com/watch?v=${vId}`
              });
            }
          }
        });
      }

      return items;
    }

    // Quét danh sách bài hát (Tab 2) - Tốc độ tức thì (0.01s) từ DOM và fallback Server
    document.getElementById('yt-btn-scan').addEventListener('click', async () => {
      // 1. Quét tức thì từ trang hiện tại (< 0.01 giây)
      const domItems = extractPlaylistFromPageDOM();
      if (domItems && domItems.length > 0) {
        renderList(domItems);
        showStatus(`✅ Đã quét ${domItems.length} bài tức thì!`, '#c2efb3');
        applyTabLayout();
        updateWindowPosition();
        return;
      }

      // 2. Nếu không tìm thấy trong DOM (hoặc URL ngoài), gọi máy chủ Python
      showStatus('⏳ Đang quét danh sách bài hát...', '#a8c7fa');
      try {
        const res = await apiFetch('/get-playlist', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: window.location.href })
        });
        const data = await res.json();
        if (res.ok && data.status === 'success') {
          try {
            renderList(data.items);
            showStatus(`✅ Tìm thấy ${data.items.length} bài!`, '#c2efb3');
            applyTabLayout();
            updateWindowPosition();
          } catch (renderErr) {
            console.error("Lỗi khi hiển thị danh sách bài hát:", renderErr);
            showStatus(`⚠️ Lỗi hiển thị danh sách: ${renderErr.message}`, '#f2b8b5');
          }
        } else {
          showStatus(`❌ ${data.message || 'Không thể quét danh sách'}`, '#f2b8b5');
        }
      } catch (e) {
        console.error("Lỗi kết nối Server Python:", e);
        showStatus('❌ Lỗi kết nối Server Python! Vui lòng kiểm tra Server đang chạy.', '#f2b8b5');
      }
    });

    // --- SPONSORBLOCK SMART SKIP FOR PREVIEW & PLAYBACK ---
    const sponsorBlockCache = new Map();
    let currentPreviewSegments = [];
    let lastSkippedSegmentEnd = -1;

    function extractVideoId(url) {
      if (!url) return null;
      try {
        if (url.includes('youtu.be/')) {
          return url.split('youtu.be/')[1].split(/[?&]/)[0].trim();
        }
        const parsed = new URL(url.startsWith('http') ? url : `https://${url}`);
        return parsed.searchParams.get('v');
      } catch (_) {
        const m = url.match(/[?&]v=([^&]+)/);
        return m ? m[1] : null;
      }
    }

    async function fetchSponsorBlockSegments(videoId) {
      if (!videoId) return [];
      if (sponsorBlockCache.has(videoId)) {
        return sponsorBlockCache.get(videoId);
      }
      try {
        const categories = JSON.stringify(["sponsor", "intro", "outro", "music_offtopic", "preview"]);
        const url = `https://sponsor.ajay.app/api/skipSegments?videoID=${encodeURIComponent(videoId)}&categories=${encodeURIComponent(categories)}`;
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          const segments = (Array.isArray(data) ? data : []).map(seg => ({
            category: seg.category,
            start: seg.segment ? seg.segment[0] : 0,
            end: seg.segment ? seg.segment[1] : 0
          })).sort((a, b) => a.start - b.start);
          sponsorBlockCache.set(videoId, segments);
          return segments;
        } else {
          sponsorBlockCache.set(videoId, []);
          return [];
        }
      } catch (_) {
        sponsorBlockCache.set(videoId, []);
        return [];
      }
    }

    function checkAndSkipSponsorBlock(audioEl, segments, showNotification = true) {
      if (!audioEl || !segments || segments.length === 0) return;
      if (!optSponsorBlock || !optSponsorBlock.checked) return;

      const curTime = audioEl.currentTime;
      for (const seg of segments) {
        if (curTime >= seg.start - 0.25 && curTime < seg.end - 0.3) {
          if (lastSkippedSegmentEnd !== seg.end) {
            lastSkippedSegmentEnd = seg.end;
            audioEl.currentTime = seg.end;
            if (showNotification) {
              showStatus(`⚡ Đã tự động bỏ qua đoạn intro / tài trợ (${formatTime(seg.start)} - ${formatTime(seg.end)})`, '#c2efb3');
            }
            break;
          }
        }
      }
    }

    function updateSponsorBlockState(enabled) {
      if (enabled && currentPreviewUrl && previewAudio) {
        const vid = extractVideoId(currentPreviewUrl);
        if (vid) {
          fetchSponsorBlockSegments(vid).then(segs => {
            currentPreviewSegments = segs;
            checkAndSkipSponsorBlock(previewAudio, segs, true);
          });
        }
      }
    }

    function updateLoudnormState(enabled) {
      // Khi tải về máy, Loudnorm được xử lý bằng FFmpeg filter EBU R128 chất lượng cao nhất.
    }

    // --- TRÌNH PHÁT NGHE THỬ ÂM THANH (TAB 2) ---
    // --- TRÌNH PHÁT NGHE THỬ ÂM THANH (TAB 2) ---
    const previewBar = document.getElementById('yt-preview-player-bar');
    const previewTitle = document.getElementById('yt-preview-title');
    const previewAudio = document.getElementById('yt-preview-audio-element');
    const previewToggleBtn = document.getElementById('yt-preview-toggle-btn');
    const previewPrevBtn = document.getElementById('yt-preview-prev-btn');
    const previewNextBtn = document.getElementById('yt-preview-next-btn');
    const previewAutoplayBtn = document.getElementById('yt-preview-autoplay-btn');
    const previewCloseBtn = document.getElementById('yt-preview-close-btn');
    const previewSeekBar = document.getElementById('yt-preview-seek-bar');
    const previewCurrentTime = document.getElementById('yt-preview-current-time');
    const previewTotalTime = document.getElementById('yt-preview-total-time');

    let currentPlaylistItems = [];
    let currentPreviewIndex = -1;
    let currentPreviewUrl = null;
    let isAutoplayEnabled = true;
    let isUserSeeking = false;

    // Trình phát iframe YouTube nhúng ngầm (không phụ thuộc bot check backend)
    let activePlayerMode = 'iframe'; // 'iframe' hoặc 'audio'
    let iframeDuration = 0;
    let iframeCurrentTime = 0;
    let iframeIsPlaying = false;

    function getOrCreatePreviewIframe() {
      let iframe = document.getElementById('yt-preview-hidden-iframe');
      if (!iframe) {
        const wrapper = document.createElement('div');
        wrapper.id = 'yt-preview-iframe-wrapper';
        wrapper.style.cssText = 'position:fixed;top:-9999px;left:-9999px;width:1px;height:1px;opacity:0;pointer-events:none;z-index:-1;';
        wrapper.innerHTML = '<iframe id="yt-preview-hidden-iframe" allow="autoplay" src="" style="width:1px;height:1px;border:none;"></iframe>';
        document.body.appendChild(wrapper);
        iframe = document.getElementById('yt-preview-hidden-iframe');
      }
      return iframe;
    }

    function sendIframeCommand(func, args = "") {
      const iframe = getOrCreatePreviewIframe();
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage(JSON.stringify({
          event: 'command',
          func: func,
          args: args
        }), '*');
      }
    }

    function formatTime(seconds) {
      if (isNaN(seconds) || seconds < 0) return "00:00";
      const m = Math.floor(seconds / 60);
      const s = Math.floor(seconds % 60);
      return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    function updateItemPlayBtns(icon) {
      document.querySelectorAll('.yt-item-play-btn').forEach(btn => {
        const parent = btn.closest('.yt-mp3-item');
        if (parent && parent.dataset.url === currentPreviewUrl) {
          btn.innerHTML = icon;
          if (icon === '⏸' || icon === '⏳') {
            btn.classList.add('playing');
          } else {
            btn.classList.remove('playing');
          }
        } else {
          btn.innerHTML = '▶';
          btn.classList.remove('playing');
        }
      });

      // Đánh dấu nổi bật bài hát đang nghe thử trong danh sách
      document.querySelectorAll('.yt-mp3-item').forEach(itemDiv => {
        if (itemDiv.dataset.url === currentPreviewUrl && currentPreviewUrl) {
          itemDiv.classList.add('active-preview');
        } else {
          itemDiv.classList.remove('active-preview');
        }
      });
    }

    function togglePreviewPlayState() {
      if (activePlayerMode === 'iframe') {
        if (iframeIsPlaying) {
          sendIframeCommand('pauseVideo');
          iframeIsPlaying = false;
          previewToggleBtn.innerHTML = '▶';
          updateItemPlayBtns('▶');
        } else {
          sendIframeCommand('playVideo');
          iframeIsPlaying = true;
          previewToggleBtn.innerHTML = '⏸';
          updateItemPlayBtns('⏸');
        }
      } else if (previewAudio) {
        if (previewAudio.paused) {
          previewAudio.play().catch(() => {});
        } else {
          previewAudio.pause();
        }
      }
    }

    function seekPreview(targetTime) {
      if (activePlayerMode === 'iframe') {
        sendIframeCommand('seekTo', [targetTime, true]);
        iframeCurrentTime = targetTime;
        previewCurrentTime.textContent = formatTime(targetTime);
      } else if (previewAudio) {
        previewAudio.currentTime = targetTime;
      }
    }

    function seekPreviewRelative(delta) {
      if (activePlayerMode === 'iframe') {
        const newT = Math.max(0, Math.min(iframeDuration || 9999, iframeCurrentTime + delta));
        seekPreview(newT);
      } else if (previewAudio && previewAudio.duration) {
        previewAudio.currentTime = Math.max(0, Math.min(previewAudio.duration, previewAudio.currentTime + delta));
      }
    }

    function startPreviewSongByIndex(index, shouldPlay = true) {
      if (!currentPlaylistItems || currentPlaylistItems.length === 0) return;
      if (index < 0) index = currentPlaylistItems.length - 1;
      if (index >= currentPlaylistItems.length) index = 0;

      currentPreviewIndex = index;
      const item = currentPlaylistItems[index];
      if (!item || !item.url) return;

      currentPreviewUrl = item.url;
      currentPreviewSegments = [];
      lastSkippedSegmentEnd = -1;

      previewTitle.textContent = `${index + 1}. ${item.title}`;
      if (previewBar) previewBar.style.display = 'flex';
      previewCurrentTime.textContent = '00:00';
      previewTotalTime.textContent = '...';
      previewSeekBar.value = 0;
      previewToggleBtn.innerHTML = '⏳';

      updateItemPlayBtns('⏳');

      // Tự động cuộn đến bài hát đang phát trong danh sách
      const allItemDivs = document.querySelectorAll('.yt-mp3-item');
      if (allItemDivs[index]) {
        allItemDivs[index].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }

      // Đồng bộ cookie phiên làm việc hiện tại của trình duyệt sang server trong nền
      try {
        chrome.runtime.sendMessage({ type: 'sync-cookies' }).catch(() => {});
      } catch (_) {}

      const videoId = extractVideoId(item.url);

      // Lấy danh sách đoạn cắt SponsorBlock nếu bật
      if (videoId && optSponsorBlock && optSponsorBlock.checked) {
        fetchSponsorBlockSegments(videoId).then(segments => {
          if (currentPreviewUrl === item.url) {
            currentPreviewSegments = segments;
            if (segments.length > 0 && segments[0].start <= 2.5) {
              const skipTo = segments[0].end;
              lastSkippedSegmentEnd = skipTo;
              seekPreview(skipTo);
              showStatus(`⚡ Bỏ qua intro, phát ngay từ ${formatTime(skipTo)}`, '#c2efb3');
            }
          }
        });
      }

      activePlayerMode = 'audio';
      const iframe = document.getElementById('yt-preview-hidden-iframe');
      if (iframe) iframe.src = '';

      if (previewAudio) {
        const volSlider = document.getElementById('yt-preview-vol-slider');
        if (volSlider) {
          previewAudio.volume = parseFloat(volSlider.value) || 1;
        }
        previewAudio.src = `${API_BASE_URL}/api/preview-stream?url=${encodeURIComponent(item.url)}`;
        previewAudio.load();
        if (shouldPlay) {
          previewAudio.play().catch(err => {
            console.log("Đang nạp luồng âm thanh nghe thử...", err);
          });
        }
      }

      // Nạp trước danh sách luồng âm thanh các bài tiếp theo vào RAM máy chủ
      const nextIdx1 = (index + 1) % currentPlaylistItems.length;
      const nextIdx2 = (index + 2) % currentPlaylistItems.length;
      const urlsToPreload = [];
      if (currentPlaylistItems[nextIdx1]?.url) urlsToPreload.push(currentPlaylistItems[nextIdx1].url);
      if (currentPlaylistItems[nextIdx2]?.url) urlsToPreload.push(currentPlaylistItems[nextIdx2].url);
      if (urlsToPreload.length > 0) {
        fetch(`${API_BASE_URL}/api/preload-playlist`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ urls: urlsToPreload })
        }).catch(() => {});
      }
    }

    // Lắng nghe sự kiện từ YouTube Embedded Player ngầm
    window.addEventListener('message', (event) => {
      if (activePlayerMode !== 'iframe') return;
      try {
        const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        if (!data) return;

        if (data.event === 'onReady') {
          const volSlider = document.getElementById('yt-preview-vol-slider');
          const vol = volSlider ? parseFloat(volSlider.value) : 1;
          sendIframeCommand('setVolume', [Math.round(vol * 100)]);
        }

        if (data.event === 'infoDelivery' && data.info) {
          if (typeof data.info.duration === 'number' && data.info.duration > 0) {
            iframeDuration = data.info.duration;
            previewTotalTime.textContent = formatTime(iframeDuration);
          }
          if (typeof data.info.currentTime === 'number') {
            iframeCurrentTime = data.info.currentTime;
            if (!isUserSeeking && iframeDuration > 0) {
              previewSeekBar.value = (iframeCurrentTime / iframeDuration) * 100;
              previewCurrentTime.textContent = formatTime(iframeCurrentTime);
              checkAndSkipSponsorBlock(null, currentPreviewSegments, true, iframeCurrentTime, (newT) => {
                seekPreview(newT);
              });
            }
          }
          if (typeof data.info.playerState === 'number') {
            const state = data.info.playerState;
            if (state === 1) { // PLAYING
              iframeIsPlaying = true;
              previewToggleBtn.innerHTML = '⏸';
              updateItemPlayBtns('⏸');
            } else if (state === 2) { // PAUSED
              iframeIsPlaying = false;
              previewToggleBtn.innerHTML = '▶';
              updateItemPlayBtns('▶');
            } else if (state === 0) { // ENDED
              iframeIsPlaying = false;
              if (isAutoplayEnabled && currentPlaylistItems.length > 0) {
                playNextPreview(true);
              } else {
                previewToggleBtn.innerHTML = '▶';
                updateItemPlayBtns('▶');
                previewSeekBar.value = 0;
                previewCurrentTime.textContent = '00:00';
              }
            }
          }
        }
      } catch (_) {}
    });

    function togglePreviewSong(item, itemBtn) {
      if (currentPreviewUrl === item.url) {
        togglePreviewPlayState();
        return;
      }

      const foundIdx = currentPlaylistItems.findIndex(x => x.url === item.url);
      startPreviewSongByIndex(foundIdx >= 0 ? foundIdx : 0, true);
    }

    function playNextPreview(isAuto = false) {
      if (!currentPlaylistItems || currentPlaylistItems.length === 0) return;
      let nextIndex = currentPreviewIndex + 1;
      if (nextIndex >= currentPlaylistItems.length) {
        nextIndex = 0; // Tự động lặp lại từ bài đầu tiên
      }
      startPreviewSongByIndex(nextIndex, true);
    }

    function playPrevPreview() {
      if (!currentPlaylistItems || currentPlaylistItems.length === 0) return;
      if ((activePlayerMode === 'iframe' && iframeCurrentTime > 3) || (activePlayerMode === 'audio' && previewAudio && previewAudio.currentTime > 3)) {
        seekPreview(0);
        return;
      }
      let prevIndex = currentPreviewIndex - 1;
      if (prevIndex < 0) {
        prevIndex = currentPlaylistItems.length - 1;
      }
      startPreviewSongByIndex(prevIndex, true);
    }

    if (previewAudio) {
      previewAudio.addEventListener('waiting', () => {
        if (activePlayerMode === 'audio') {
          previewToggleBtn.innerHTML = '⏳';
          updateItemPlayBtns('⏳');
        }
      });

      previewAudio.addEventListener('canplay', () => {
        if (activePlayerMode === 'audio' && !previewAudio.paused) {
          previewToggleBtn.innerHTML = '⏸';
          updateItemPlayBtns('⏸');
        }
      });

      previewAudio.addEventListener('playing', () => {
        if (activePlayerMode === 'audio') {
          previewToggleBtn.innerHTML = '⏸';
          updateItemPlayBtns('⏸');
        }
      });

      previewAudio.addEventListener('pause', () => {
        if (activePlayerMode === 'audio') {
          previewToggleBtn.innerHTML = '▶';
          updateItemPlayBtns('▶');
        }
      });

      previewAudio.addEventListener('error', (e) => {
        if (activePlayerMode === 'audio') {
          console.warn("Lỗi tải audio preview:", e);
          previewToggleBtn.innerHTML = '▶';
          updateItemPlayBtns('▶');
          showStatus('⚠️ Nguồn đang kết nối lại, vui lòng bấm ▶ thử lại!', '#f2b8b5');
        }
      });

      previewAudio.addEventListener('ended', () => {
        if (activePlayerMode === 'audio') {
          if (isAutoplayEnabled && currentPlaylistItems.length > 0) {
            playNextPreview(true);
          } else {
            previewToggleBtn.innerHTML = '▶';
            updateItemPlayBtns('▶');
            previewSeekBar.value = 0;
            previewCurrentTime.textContent = '00:00';
          }
        }
      });

      previewAudio.addEventListener('timeupdate', () => {
        if (activePlayerMode === 'audio' && !isUserSeeking && previewAudio.duration) {
          const percent = (previewAudio.currentTime / previewAudio.duration) * 100;
          previewSeekBar.value = percent;
          previewCurrentTime.textContent = formatTime(previewAudio.currentTime);
          checkAndSkipSponsorBlock(previewAudio, currentPreviewSegments, true);
        }
      });

      previewAudio.addEventListener('loadedmetadata', () => {
        if (activePlayerMode === 'audio' && previewAudio.duration) {
          previewTotalTime.textContent = formatTime(previewAudio.duration);
        }
      });

      previewAudio.addEventListener('durationchange', () => {
        if (activePlayerMode === 'audio' && previewAudio.duration) {
          previewTotalTime.textContent = formatTime(previewAudio.duration);
        }
      });
    }

    if (previewToggleBtn) {
      previewToggleBtn.addEventListener('click', () => {
        if (!currentPreviewUrl) {
          if (currentPlaylistItems.length > 0) {
            startPreviewSongByIndex(0, true);
          }
          return;
        }
        togglePreviewPlayState();
      });
    }

    if (previewPrevBtn) {
      previewPrevBtn.addEventListener('click', () => {
        playPrevPreview();
      });
    }

    if (previewNextBtn) {
      previewNextBtn.addEventListener('click', () => {
        playNextPreview(false);
      });
    }

    if (previewAutoplayBtn) {
      previewAutoplayBtn.addEventListener('click', () => {
        isAutoplayEnabled = !isAutoplayEnabled;
        previewAutoplayBtn.classList.toggle('active', isAutoplayEnabled);
        previewAutoplayBtn.title = isAutoplayEnabled 
          ? "Tự động phát bài tiếp theo (Đang Bật)" 
          : "Tự động phát bài tiếp theo (Đang Tắt)";
      });
    }

    if (previewCloseBtn) {
      previewCloseBtn.addEventListener('click', () => {
        const iframe = document.getElementById('yt-preview-hidden-iframe');
        if (iframe) iframe.src = '';
        if (previewAudio) {
          previewAudio.pause();
          previewAudio.src = '';
        }
        iframeIsPlaying = false;
        currentPreviewUrl = null;
        currentPreviewIndex = -1;
        if (previewBar) previewBar.style.display = 'none';
        updateItemPlayBtns('▶');
      });
    }

    // --- THANH ÂM LƯỢNG NGHE THỬ ---
    const previewVolBtn = document.getElementById('yt-preview-vol-btn');
    const previewVolSlider = document.getElementById('yt-preview-vol-slider');

    if (previewVolSlider) {
      const savedVol = localStorage.getItem('mallios_preview_vol');
      if (savedVol !== null) {
        previewVolSlider.value = savedVol;
        if (previewAudio) previewAudio.volume = parseFloat(savedVol);
      }
      previewVolSlider.addEventListener('input', () => {
        const vol = parseFloat(previewVolSlider.value);
        if (previewAudio) previewAudio.volume = vol;
        sendIframeCommand('setVolume', [Math.round(vol * 100)]);
        localStorage.setItem('mallios_preview_vol', String(vol));
        if (previewVolBtn) previewVolBtn.textContent = vol === 0 ? '🔇' : (vol < 0.5 ? '🔉' : '🔊');
      });
    }

    if (previewVolBtn && previewVolSlider) {
      previewVolBtn.addEventListener('click', () => {
        const curVol = parseFloat(previewVolSlider.value);
        if (curVol > 0) {
          previewVolBtn.dataset.lastVol = String(curVol);
          previewVolSlider.value = 0;
          if (previewAudio) previewAudio.volume = 0;
          sendIframeCommand('setVolume', [0]);
          previewVolBtn.textContent = '🔇';
        } else {
          const lastVol = parseFloat(previewVolBtn.dataset.lastVol || '1');
          previewVolSlider.value = lastVol;
          if (previewAudio) previewAudio.volume = lastVol;
          sendIframeCommand('setVolume', [Math.round(lastVol * 100)]);
          previewVolBtn.textContent = lastVol < 0.5 ? '🔉' : '🔊';
        }
      });
    }

    if (previewSeekBar) {
      previewSeekBar.addEventListener('mousedown', () => { isUserSeeking = true; });
      previewSeekBar.addEventListener('touchstart', () => { isUserSeeking = true; });

      previewSeekBar.addEventListener('input', () => {
        const dur = activePlayerMode === 'iframe' ? iframeDuration : (previewAudio ? previewAudio.duration : 0);
        if (dur) {
          const targetTime = (previewSeekBar.value / 100) * dur;
          previewCurrentTime.textContent = formatTime(targetTime);
        }
      });

      previewSeekBar.addEventListener('change', () => {
        const dur = activePlayerMode === 'iframe' ? iframeDuration : (previewAudio ? previewAudio.duration : 0);
        if (dur) {
          const targetTime = (previewSeekBar.value / 100) * dur;
          seekPreview(targetTime);
        }
        isUserSeeking = false;
      });
    }

    // --- Ô TÌM KIẾM / LỌC BÀI HÁT TRONG PLAYLIST ---
    const playlistSearchInput = document.getElementById('yt-playlist-search-input');
    const playlistSearchBox = document.getElementById('yt-search-filter-box');
    const playlistSearchClear = document.getElementById('yt-playlist-search-clear');

    if (playlistSearchInput) {
      playlistSearchInput.addEventListener('input', () => {
        const query = playlistSearchInput.value.toLowerCase().trim();
        const container = document.getElementById('yt-list-container');
        if (!container) return;
        const items = container.querySelectorAll('.yt-mp3-item');
        items.forEach(el => {
          const title = (el.dataset.title || '').toLowerCase();
          const isMatch = !query || title.includes(query);
          el.style.display = isMatch ? 'flex' : 'none';
        });
      });
    }

    if (playlistSearchClear && playlistSearchInput) {
      playlistSearchClear.addEventListener('click', () => {
        playlistSearchInput.value = '';
        playlistSearchInput.dispatchEvent(new Event('input'));
      });
    }

    function renderList(items) {
      const container = document.getElementById('yt-list-container');
      tabSelect.dataset.listReady = 'true';
      document.getElementById('yt-list-section').style.display = 'flex';
      if (playlistSearchBox) playlistSearchBox.style.display = 'flex';
      applyTabLayout();
      const curSavedHeight = localStorage.getItem('yt-mp3-height');
      if (!curSavedHeight || parseInt(curSavedHeight) < 650) {
        win.style.height = `${Math.min(750, Math.round(window.innerHeight * 0.92))}px`;
      }
      updateWindowPosition();
      container.innerHTML = '';

      const uniqueItems = [];
      const seenUrls = new Set();
      (Array.isArray(items) ? items : []).forEach(item => {
        if (!item || !item.url) return;
        const normalizedUrl = item.url.split('&')[0].trim();
        if (!seenUrls.has(normalizedUrl)) {
          seenUrls.add(normalizedUrl);
          uniqueItems.push(item);
        }
      });

      currentPlaylistItems = uniqueItems;
      if (currentPreviewUrl) {
        currentPreviewIndex = currentPlaylistItems.findIndex(x => x.url === currentPreviewUrl);
      }

      uniqueItems.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'yt-mp3-item';
        if (item.url === currentPreviewUrl) {
          div.classList.add('active-preview');
        }
        div.dataset.url = item.url;
        div.dataset.title = item.title;

        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.value = item.url;

        const playBtn = document.createElement('button');
        playBtn.type = 'button';
        playBtn.className = 'yt-item-play-btn';
        playBtn.title = 'Nghe thử bài này';
        playBtn.innerHTML = (item.url === currentPreviewUrl && previewAudio && !previewAudio.paused) ? '⏸' : '▶';

        const span = document.createElement('span');
        span.className = 'yt-item-title';
        span.innerText = `${index + 1}. ${item.title}`;

        div.appendChild(cb);
        div.appendChild(playBtn);
        div.appendChild(span);

        playBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          togglePreviewSong(item, playBtn);
        });

        // Nạp trước ngầm khi di chuột vào bài hát để bấm là phát ngay
        div.addEventListener('mouseenter', () => {
          if (item && item.url) {
            fetch(`${API_BASE_URL}/api/preview-stream?url=${encodeURIComponent(item.url)}`).catch(() => {});
          }
        }, { once: true });

        cb.addEventListener('change', () => {
          div.classList.toggle('selected', cb.checked);
          updateCount();
        });

        div.addEventListener('click', (e) => {
          if (e.target !== cb && e.target !== playBtn) {
            cb.checked = !cb.checked;
            div.classList.toggle('selected', cb.checked);
            updateCount();
          }
        });

        container.appendChild(div);
      });

      // Tự động kiểm tra trùng lặp nhanh và gắn huy hiệu ✅ Đã có
      const allUrls = uniqueItems.map(i => i.url).filter(Boolean);
      if (allUrls.length > 0) {
        apiFetch('/api/check-duplicates-batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            urls: allUrls,
            save_folder: pathInput.value.trim(),
            save_target: currentStorageTarget
          })
        }).then(r => r.json()).then(res => {
          if (res.status === 'success' && res.duplicates) {
            uniqueItems.forEach(item => {
              if (res.duplicates[item.url]) {
                const itemDiv = container.querySelector(`.yt-mp3-item[data-url="${CSS.escape(item.url)}"]`);
                if (itemDiv && !itemDiv.querySelector('.yt-badge-downloaded')) {
                  const badge = document.createElement('span');
                  badge.className = 'yt-badge-downloaded';
                  badge.innerText = '✅ Đã có';
                  const titleEl = itemDiv.querySelector('.yt-item-title');
                  if (titleEl) titleEl.appendChild(badge);
                }
              }
            });
          }
        }).catch(() => {});

        // Nạp ngầm vào RAM Server
        apiFetch('/api/preload-playlist', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ urls: allUrls })
        }).catch(() => {});
      }

      const selectAllBtn = document.getElementById('yt-select-all');
      let isAllSelected = false;
      if (selectAllBtn) {
        selectAllBtn.innerText = "Chọn tất cả";
        selectAllBtn.onclick = () => {
          isAllSelected = !isAllSelected;
          const checkboxes = container.querySelectorAll('input[type="checkbox"]');
          checkboxes.forEach(cb => {
            const parentDiv = cb.closest('.yt-mp3-item');
            if (parentDiv && parentDiv.style.display !== 'none') {
              cb.checked = isAllSelected;
              parentDiv.classList.toggle('selected', isAllSelected);
            }
          });
          selectAllBtn.innerText = isAllSelected ? "Bỏ chọn tất cả" : "Chọn tất cả";
          updateCount();
        };
      }

      updateCount();
    }

    function updateCount() {
      const selected = document.querySelectorAll('#yt-list-container input[type="checkbox"]:checked');
      const countSpan = document.getElementById('yt-select-count');
      if (countSpan) countSpan.innerText = selected.length;
    }

    // Tải Đã Chọn (Tab 2)
    document.getElementById('yt-btn-download-selected').addEventListener('click', function () {
      const btn = this;
      const selected = Array.from(document.querySelectorAll('#yt-list-container input[type="checkbox"]:checked')).map(cb => cb.value);
      const quality = document.getElementById('yt-quality-select').value;
      const savePath = pathInput.value.trim();

      if (!selected.length) return showStatus('Vui lòng chọn bài!', '#f2b8b5');

      if (currentStorageTarget === 'drive' && !isDriveConnected) {
        showStatus('⚠️ Bạn chưa kết nối Google Drive. Hãy bấm nút Kết nối ở trên!', '#f2b8b5');
        return;
      }

      const originalContent = `${SVG.check} Tải đã chọn ( <span id="yt-select-count">${selected.length}</span> )`;

      performDownload({
        links: selected,
        max_files: 0,
        quality: quality,
        download_path: savePath,
        save_target: currentStorageTarget,
        ...getDownloadOptions()
      }, btn, originalContent);
    });

    function escapeHtml(text) {
      return String(text)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
    }

    function showStatus(msg, color) {
      const st = document.getElementById('yt-mp3-status');
      if (st) {
        st.textContent = msg;
        st.style.color = color;
      }
    }

    function renderDuplicateList(duplicateFiles = []) {
      const box = document.getElementById('yt-duplicate-box');
      const title = document.getElementById('yt-duplicate-title');
      const list = document.getElementById('yt-duplicate-list');
      if (!box || !list) return;

      const matches = Array.isArray(duplicateFiles) ? duplicateFiles : [];
      if (!matches.length) {
        list.innerHTML = '';
        box.style.display = 'none';
        if (title) title.textContent = 'Danh sách trùng';
        return;
      }

      if (title) title.textContent = `Danh sách trùng (${matches.length} file khớp)`;
      list.innerHTML = matches.map((item, index) => {
        const pathLabel = item.relative_path || item.name || item.path || `File ${index + 1}`;
        return `
          <div class="yt-duplicate-item">
            <div class="yt-duplicate-index">${index + 1}</div>
            <div class="yt-duplicate-text">${escapeHtml(pathLabel)}</div>
          </div>
        `;
      }).join('');
      box.style.display = 'flex';
    }

    // --- TAB LỊCH SỬ & PHÁT NHẠC ---
    const historyList = document.getElementById('yt-history-list');
    const historyPlayer = document.getElementById('yt-history-player');
    const playBtn = document.getElementById('yt-player-play-btn');
    const playerTitle = document.getElementById('yt-player-title');
    const audioElement = document.getElementById('yt-audio-element');
    const syncHistoryBtn = document.getElementById('yt-btn-sync-history');
    const historyTotalCount = document.getElementById('yt-history-total-count');

    let currentPlayingItem = null;

    if (syncHistoryBtn) {
      syncHistoryBtn.addEventListener('click', async () => {
        const origText = syncHistoryBtn.innerHTML;
        syncHistoryBtn.innerHTML = '⏳ Đang quét...';
        syncHistoryBtn.disabled = true;
        showStatus('⏳ Đang đồng bộ và quét lại thư mục nhạc...', '#a8c7fa');
        
        try {
          const res = await apiFetch('/sync-history', {
            method: 'POST',
            body: JSON.stringify({
              download_path: pathInput ? pathInput.value.trim() : ''
            })
          });
          const data = await res.json();
          if (data.status === 'success' && data.history) {
            renderHistoryList(data.history);
            const addedMsg = (data.added_count && data.added_count > 0) ? ` (+${data.added_count} mới)` : '';
            const removedMsg = (data.removed_count && data.removed_count > 0) ? ` (-${data.removed_count} đã xóa)` : '';
            showStatus(`✅ Đã đồng bộ ${data.history.length} bài hát!${addedMsg}${removedMsg}`, '#c2efb3');
          } else {
            showStatus('⚠️ Không thể đồng bộ lịch sử.', '#f2b8b5');
          }
        } catch (_) {
          showStatus('❌ Lỗi kết nối khi đồng bộ!', '#f2b8b5');
        } finally {
          syncHistoryBtn.innerHTML = origText;
          syncHistoryBtn.disabled = false;
        }
      });
    }

    async function loadHistoryList() {
      try {
        const res = await apiFetch('/history');
        const data = await res.json();
        if (data.status === 'success' && data.history) {
          renderHistoryList(data.history);
        }
      } catch (_) {
        historyList.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #f2b8b5; text-align: center; font-size: 11px;">Không thể tải lịch sử.</div>';
      }
    }

    function renderHistoryList(history) {
      const hasHistory = Array.isArray(history) && history.length > 0;
      tabHistory.dataset.historyReady = hasHistory ? 'true' : 'false';
      if (historyTotalCount) {
        historyTotalCount.innerText = `${Array.isArray(history) ? history.length : 0} bài`;
      }

      if (!hasHistory) {
        historyList.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #8e9099; text-align: center; font-size: 11px;">Chưa có lịch sử tải nhạc.</div>';
        if (tabHistory.classList.contains('active')) {
          applyTabLayout();
          updateWindowPosition();
        }
        return;
      }

      historyList.innerHTML = '';
      history.forEach(item => {
        const div = document.createElement('div');
        div.className = 'yt-mp3-item';
        div.style.display = 'flex';
        div.style.alignItems = 'center';
        div.style.justifyContent = 'space-between';
        div.style.padding = '6px 8px';
        div.style.background = '#282930';
        div.style.border = '1px solid #3c3d45';
        div.style.borderRadius = '6px';
        div.style.gap = '8px';

        const playIcon = (currentPlayingItem && currentPlayingItem.url === item.url && !audioElement.paused) ? '⏸' : '▶';
        const playButton = document.createElement('button');
        playButton.className = 'yt-mp3-icon-btn';
        playButton.style.width = '24px';
        playButton.style.height = '24px';
        playButton.style.background = '#a8c7fa';
        playButton.style.color = '#1c1b1f';
        playButton.style.fontSize = '9px';
        playButton.innerText = playIcon;
        playButton.onclick = () => togglePlayItem(item, playButton);

        const infoDiv = document.createElement('div');
        infoDiv.style.flex = '1';
        infoDiv.style.minWidth = '0';
        infoDiv.style.display = 'flex';
        infoDiv.style.flexDirection = 'column';
        infoDiv.style.gap = '2px';
        
        const titleSpan = document.createElement('span');
        titleSpan.style.color = '#e3e3e3';
        titleSpan.style.fontSize = '10px';
        titleSpan.style.fontWeight = 'bold';
        titleSpan.style.overflow = 'hidden';
        titleSpan.style.textOverflow = 'ellipsis';
        titleSpan.style.whiteSpace = 'nowrap';
        titleSpan.innerText = item.title;

        const artistSpan = document.createElement('span');
        artistSpan.style.color = '#8e9099';
        artistSpan.style.fontSize = '9px';
        artistSpan.style.overflow = 'hidden';
        artistSpan.style.textOverflow = 'ellipsis';
        artistSpan.style.whiteSpace = 'nowrap';
        artistSpan.innerText = item.uploader;

        infoDiv.appendChild(titleSpan);
        infoDiv.appendChild(artistSpan);

        const isDrive = item.storage_type === 'drive' || !!item.drive_web_link;
        if (isDrive) {
          const badge = document.createElement('span');
          badge.className = 'yt-drive-badge';
          badge.innerText = '☁️ Drive';
          titleSpan.appendChild(badge);
        }

        const ctrlDiv = document.createElement('div');
        ctrlDiv.style.display = 'flex';
        ctrlDiv.style.alignItems = 'center';
        ctrlDiv.style.gap = '4px';

        // Nút QR Code để quét nghe/tải trên điện thoại (cùng mạng Wi-Fi)
        const qrBtn = document.createElement('button');
        qrBtn.className = 'yt-qr-btn';
        qrBtn.innerHTML = '📱 QR';
        qrBtn.title = 'Quét mã QR nghe / tải ngay trên điện thoại';
        qrBtn.onclick = (e) => {
          e.stopPropagation();
          showQrCodeModal(item);
        };

        const folderBtn = document.createElement('button');
        folderBtn.className = 'yt-mp3-icon-btn';
        folderBtn.style.width = '24px';
        folderBtn.style.height = '24px';
        folderBtn.innerHTML = isDrive ? SVG.drive : SVG.folder;
        folderBtn.title = isDrive ? 'Mở bài hát trên Google Drive' : 'Mở thư mục chứa file';
        folderBtn.onclick = async () => {
          if (isDrive && item.drive_web_link) {
            window.open(item.drive_web_link, '_blank');
            return;
          }
          try {
            await apiFetch('/open-folder', {
              method: 'POST',
              body: JSON.stringify({ path: item.file_path, drive_link: item.drive_web_link })
            });
          } catch (_) {
            showStatus('❌ Không thể mở thư mục!', '#f2b8b5');
          }
        };

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'yt-mp3-icon-btn';
        deleteBtn.style.width = '24px';
        deleteBtn.style.height = '24px';
        deleteBtn.innerHTML = SVG.close;
        deleteBtn.title = 'Xóa khỏi lịch sử';
        deleteBtn.onclick = () => askDeleteHistory(item);

        ctrlDiv.appendChild(qrBtn);
        ctrlDiv.appendChild(folderBtn);
        ctrlDiv.appendChild(deleteBtn);

        div.appendChild(playButton);
        div.appendChild(infoDiv);
        div.appendChild(ctrlDiv);

        historyList.appendChild(div);
      });

      currentHistoryList = history;
      if (currentPlayingItem) {
        currentHistoryIndex = currentHistoryList.findIndex(x => x.url === currentPlayingItem.url);
      }

      if (tabHistory.classList.contains('active')) {
        applyTabLayout();
        updateWindowPosition();
      }
    }

    // Modal hiển thị mã QR Code chia sẻ bài hát nội bộ
    async function showQrCodeModal(item) {
      let localIp = '127.0.0.1';
      let port = 37491;
      try {
        const res = await apiFetch('/api/local-ip');
        const data = await res.json();
        if (data.status === 'success' && data.ip) {
          localIp = data.ip;
          port = data.port || 37491;
        }
      } catch (_) {}

      const isDrive = item.storage_type === 'drive' || !item.file_path;
      let shareUrl = '';
      if (isDrive && item.drive_web_link) {
        shareUrl = item.drive_web_link;
      } else if (item.file_path) {
        shareUrl = `http://${localIp}:${port}/play?path=${encodeURIComponent(item.file_path)}`;
      } else {
        shareUrl = `http://${localIp}:${port}/api/preview-stream?url=${encodeURIComponent(item.url)}`;
      }

      const qrImgUrl = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(shareUrl)}`;

      const modal = document.createElement('div');
      modal.className = 'yt-qr-modal';
      modal.innerHTML = `
        <div class="yt-qr-card">
          <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
            <span style="font-weight: bold; font-size: 12px; color: #a8c7fa;">📱 Quét Mã Nghe Trên Điện Thoại</span>
            <button id="yt-qr-close" style="background: transparent; border: none; color: #8e9099; cursor: pointer; font-size: 14px;">✕</button>
          </div>
          <div style="font-size: 10px; color: #c4c6d0; line-height: 1.3; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            ${escapeHtml(item.title)}
          </div>
          <div style="background: #fff; padding: 6px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <img src="${qrImgUrl}" width="160" height="160" alt="QR Code" style="display: block; border-radius: 4px;">
          </div>
          <div style="font-size: 9.5px; color: #8e9099; line-height: 1.4;">
            💡 Đảm bảo điện thoại và máy tính kết nối <b style="color: #c2efb3;">cùng mạng Wi-Fi</b> để nghe / tải trực tiếp.
          </div>
          <button id="yt-qr-copy-btn" style="background: #2b2c34; border: 1px solid rgba(255,255,255,0.15); color: #e2e2e9; font-size: 10px; padding: 4px 10px; border-radius: 6px; cursor: pointer; width: 100%;">
            📋 Sao chép link bài hát
          </button>
        </div>
      `;

      document.body.appendChild(modal);

      modal.querySelector('#yt-qr-close').onclick = () => modal.remove();
      modal.onclick = (e) => { if (e.target === modal) modal.remove(); };

      modal.querySelector('#yt-qr-copy-btn').onclick = function () {
        navigator.clipboard.writeText(shareUrl).then(() => {
          this.textContent = '✅ Đã sao chép link!';
          setTimeout(() => { if (this) this.textContent = '📋 Sao chép link bài hát'; }, 2000);
        });
      };
    }

    const playerCloseBtn = document.getElementById('yt-player-close-btn');
    const playerSeekBar = document.getElementById('yt-player-seek-bar');
    const playerCurrentTime = document.getElementById('yt-player-current-time');
    const playerTotalTime = document.getElementById('yt-player-total-time');
    const historyAutoplayBtn = document.getElementById('yt-history-autoplay-btn');
    const historyPrevBtn = document.getElementById('yt-history-prev-btn');
    const historyNextBtn = document.getElementById('yt-history-next-btn');

    let isHistoryAutoplayEnabled = true;
    let currentHistoryList = [];
    let currentHistoryIndex = -1;
    let isHistoryUserSeeking = false;

    function playHistoryTrackByIndex(index) {
      if (!currentHistoryList || currentHistoryList.length === 0) return;
      if (index < 0) index = currentHistoryList.length - 1;
      if (index >= currentHistoryList.length) index = 0;

      currentHistoryIndex = index;
      const item = currentHistoryList[index];
      if (item) {
        togglePlayItem(item, null, true);
      }
    }

    function playNextHistoryTrack() {
      if (!currentHistoryList || currentHistoryList.length === 0) return;
      playHistoryTrackByIndex(currentHistoryIndex + 1);
    }

    function playPrevHistoryTrack() {
      if (!currentHistoryList || currentHistoryList.length === 0) return;
      if (audioElement && audioElement.currentTime > 3) {
        audioElement.currentTime = 0;
        audioElement.play().catch(() => {});
        return;
      }
      playHistoryTrackByIndex(currentHistoryIndex - 1);
    }

    if (historyAutoplayBtn) {
      historyAutoplayBtn.addEventListener('click', () => {
        isHistoryAutoplayEnabled = !isHistoryAutoplayEnabled;
        historyAutoplayBtn.classList.toggle('active', isHistoryAutoplayEnabled);
        historyAutoplayBtn.title = isHistoryAutoplayEnabled 
          ? "Tự động phát bài tiếp trong Lịch sử (Đang Bật)" 
          : "Tự động phát bài tiếp trong Lịch sử (Đang Tắt)";
      });
    }

    if (historyPrevBtn) {
      historyPrevBtn.addEventListener('click', () => playPrevHistoryTrack());
    }

    if (historyNextBtn) {
      historyNextBtn.addEventListener('click', () => playNextHistoryTrack());
    }

    function togglePlayItem(item, button, forcePlay = false) {
      if (currentPlayingItem && currentPlayingItem.url === item.url && !forcePlay) {
        if (audioElement.paused) {
          audioElement.play().catch(() => {});
          if (button) button.innerText = '⏸';
          playBtn.innerText = '⏸';
        } else {
          audioElement.pause();
          if (button) button.innerText = '▶';
          playBtn.innerText = '▶';
        }
      } else {
        currentPlayingItem = item;
        currentHistoryIndex = currentHistoryList.findIndex(x => x.url === item.url);
        playerTitle.innerText = item.title;
        historyPlayer.style.display = 'flex';
        playerCurrentTime.innerText = '00:00';
        playerTotalTime.innerText = '...';
        playerSeekBar.value = 0;
        playBtn.innerText = '⏳';
        if (button) button.innerText = '⏳';
        
        const isDrive = item.storage_type === 'drive' || !item.file_path;
        if (isDrive) {
          audioElement.src = `${API_BASE_URL}/api/preview-stream?url=${encodeURIComponent(item.url)}`;
        } else {
          audioElement.src = `${API_BASE_URL}/play?path=${encodeURIComponent(item.file_path)}`;
        }
        
        const dsp = getOrCreateAudioDSP(audioElement);
        if (dsp) {
          dsp.resume();
          dsp.applyState(optLoudnorm ? optLoudnorm.checked : false);
        }

        audioElement.load();
        audioElement.play().catch(err => {
          console.warn("Lỗi phát audio local, fallback stream:", err);
          audioElement.src = `${API_BASE_URL}/api/preview-stream?url=${encodeURIComponent(item.url)}`;
          audioElement.play().catch(() => {});
        });
        
        loadHistoryList();
      }
    }

    if (playerCloseBtn) {
      playerCloseBtn.addEventListener('click', () => {
        audioElement.pause();
        audioElement.src = '';
        currentPlayingItem = null;
        historyPlayer.style.display = 'none';
        loadHistoryList();
      });
    }

    if (playerSeekBar) {
      playerSeekBar.addEventListener('mousedown', () => { isHistoryUserSeeking = true; });
      playerSeekBar.addEventListener('touchstart', () => { isHistoryUserSeeking = true; });

      playerSeekBar.addEventListener('input', () => {
        if (audioElement.duration) {
          const targetTime = (playerSeekBar.value / 100) * audioElement.duration;
          playerCurrentTime.innerText = formatTime(targetTime);
        }
      });

      playerSeekBar.addEventListener('change', () => {
        if (audioElement.duration) {
          audioElement.currentTime = (playerSeekBar.value / 100) * audioElement.duration;
        }
        isHistoryUserSeeking = false;
      });
    }

    function askDeleteHistory(item) {
      const check = confirm(`Bạn có muốn xóa bài hát "${item.title}" khỏi lịch sử?`);
      if (check) {
        const deleteFile = confirm("Bạn có muốn XÓA HẲN tệp tin nhạc MP3 này trên máy tính của bạn không?");
        performDeleteHistory(item, deleteFile);
      }
    }

    async function performDeleteHistory(item, deleteFile) {
      try {
        const res = await apiFetch('/delete-history', {
          method: 'POST',
          body: JSON.stringify({
            url: item.url,
            delete_file: deleteFile,
            file_path: item.file_path
          })
        });
        const data = await res.json();
        if (data.status === 'success') {
          if (currentPlayingItem && currentPlayingItem.url === item.url) {
            audioElement.pause();
            historyPlayer.style.display = 'none';
            currentPlayingItem = null;
          }
          loadHistoryList();
          showStatus('✅ Đã xóa thành công.', '#c2efb3');
        }
      } catch (_) {
        showStatus('❌ Xóa thất bại!', '#f2b8b5');
      }
    }

    audioElement.addEventListener('timeupdate', () => {
      if (!isHistoryUserSeeking && audioElement.duration) {
        const percent = (audioElement.currentTime / audioElement.duration) * 100;
        playerSeekBar.value = percent;
        playerCurrentTime.innerText = formatTime(audioElement.currentTime);
      }
    });

    audioElement.addEventListener('loadedmetadata', () => {
      if (audioElement.duration) {
        playerTotalTime.innerText = formatTime(audioElement.duration);
      }
    });

    audioElement.addEventListener('durationchange', () => {
      if (audioElement.duration) {
        playerTotalTime.innerText = formatTime(audioElement.duration);
      }
    });

    audioElement.addEventListener('play', () => {
      playBtn.innerText = '⏸';
      loadHistoryList();
    });

    audioElement.addEventListener('pause', () => {
      playBtn.innerText = '▶';
      loadHistoryList();
    });

    audioElement.addEventListener('ended', () => {
      if (isHistoryAutoplayEnabled && currentHistoryList.length > 0) {
        playNextHistoryTrack();
      } else {
        playBtn.innerText = '▶';
        currentPlayingItem = null;
        historyPlayer.style.display = 'none';
        loadHistoryList();
      }
    });

    playBtn.onclick = () => {
      if (audioElement.src) {
        if (audioElement.paused) {
          audioElement.play().catch(() => {});
        } else {
          audioElement.pause();
        }
      }
    };

    // --- PHÍM TẮT ĐIỀU KHIỂN NHANH (KEYBOARD SHORTCUTS) ---
    window.addEventListener('keydown', (e) => {
      const isInputFocused = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName);
      if (isInputFocused) return;
      if (!win || !win.classList.contains('active')) return;

      if (e.code === 'Space') {
        e.preventDefault();
        if (previewBar && previewBar.style.display !== 'none') {
          togglePreviewPlayState();
        } else if (audioElement && audioElement.src && historyPlayer && historyPlayer.style.display !== 'none') {
          if (audioElement.paused) audioElement.play().catch(() => {});
          else audioElement.pause();
        }
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        if (previewBar && previewBar.style.display !== 'none') {
          seekPreviewRelative(-5);
        } else if (audioElement && audioElement.duration && historyPlayer && historyPlayer.style.display !== 'none') {
          audioElement.currentTime = Math.max(0, audioElement.currentTime - 5);
        }
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        if (previewBar && previewBar.style.display !== 'none') {
          seekPreviewRelative(5);
        } else if (audioElement && audioElement.duration && historyPlayer && historyPlayer.style.display !== 'none') {
          audioElement.currentTime = Math.min(audioElement.duration, audioElement.currentTime + 5);
        }
      } else if (e.code === 'KeyN') {
        if (previewBar && previewBar.style.display !== 'none') playNextPreview();
        else if (historyPlayer && historyPlayer.style.display !== 'none') playNextHistoryTrack();
      } else if (e.code === 'KeyP') {
        if (previewBar && previewBar.style.display !== 'none') playPrevPreview();
        else if (historyPlayer && historyPlayer.style.display !== 'none') playPrevHistoryTrack();
      }
    });

  } catch (err) {
    console.error("Lỗi MP3 Extension:", err);
  }
})();