const NATIVE_HOST = "com.mallios.mp3";
const API_BASE_URL = "http://127.0.0.1:37491";

let nativePort = null;
let pendingEnsurePromise = null;

function ensureBackendRunning() {
  if (pendingEnsurePromise) {
    return pendingEnsurePromise;
  }

  pendingEnsurePromise = new Promise((resolve) => {
    try {
      if (!nativePort) {
        nativePort = chrome.runtime.connectNative(NATIVE_HOST);
        nativePort.onMessage.addListener((message) => {
          console.log("[Mallios] Native Host Response:", message);
          if (message && message.ok) {
            resolve({ ok: true, status: message.status || "online" });
          }
        });
        nativePort.onDisconnect.addListener(() => {
          const err = chrome.runtime.lastError?.message;
          console.warn("[Mallios] Native Host Disconnected:", err);
          nativePort = null;
          resolve({ ok: false, error: err });
        });
      }
      
      nativePort.postMessage({ command: "ensure-running" });
      
      // Fallback timeout sau 3.5s neu Native Host khong phan hoi kip
      setTimeout(() => {
        resolve({ ok: true });
      }, 3500);
      
    } catch (err) {
      console.error("[Mallios] Exception calling connectNative:", err);
      nativePort = null;
      resolve({ ok: false, error: err.message });
    }
  }).finally(() => {
    setTimeout(() => {
      pendingEnsurePromise = null;
    }, 1000);
  });

  return pendingEnsurePromise;
}

async function proxyApiRequest(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const fetchOptions = {
    method: options.method || "GET",
    headers: options.headers || { "Content-Type": "application/json" }
  };
  if (options.body) {
    fetchOptions.body = options.body;
  }

  try {
    const res = await fetch(url, fetchOptions);
    const text = await res.text();
    return { ok: res.ok, status: res.status, body: text };
  } catch (initialError) {
    // Tu dong kich hoat server qua Native Host va doi
    await ensureBackendRunning();

    // Cho toi da 6 giay (12 lan x 500ms) de may chu boot xong
    for (let attempt = 0; attempt < 12; attempt++) {
      await new Promise((r) => setTimeout(r, 500));
      try {
        const retryRes = await fetch(url, fetchOptions);
        const retryText = await retryRes.text();
        return { ok: retryRes.ok, status: retryRes.status, body: retryText };
      } catch (_) {}
    }
    return { 
      ok: false, 
      status: 503, 
      body: JSON.stringify({ status: "error", message: "Máy chủ Mallios chưa bật. Vui lòng mở tệp run.bat trong thư mục Mallios." }) 
    };
  }
}

async function checkServerHealth(autoWake = true) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/status`, { method: "GET" });
    if (res.ok) {
      return { ok: true, online: true };
    }
  } catch (_) {}

  // Neu server chua bat va autoWake = true, tu dong danh thuc ngam
  if (autoWake) {
    ensureBackendRunning();
    for (let attempt = 0; attempt < 6; attempt++) {
      await new Promise((r) => setTimeout(r, 500));
      try {
        const retryRes = await fetch(`${API_BASE_URL}/api/status`, { method: "GET" });
        if (retryRes.ok) {
          return { ok: true, online: true };
        }
      } catch (_) {}
    }
  }

  return { ok: false, online: false };
}
async function loginWithGoogleIdentity() {
  return new Promise((resolve) => {
    try {
      if (chrome.identity && chrome.identity.getAuthToken) {
        chrome.identity.getAuthToken({ interactive: true }, async (token) => {
          if (chrome.runtime.lastError || !token) {
            const err = chrome.runtime.lastError?.message || "Không nhận được token từ Chrome";
            console.warn("[Mallios] chrome.identity error:", err);
            resolve({ ok: false, error: err });
          } else {
            const setRes = await proxyApiRequest("/auth/google/set-token", {
              method: "POST",
              body: JSON.stringify({ access_token: token })
            });
            let data = {};
            try { data = JSON.parse(setRes.body); } catch (_) {}
            resolve({ ok: setRes.ok, status: setRes.status, data: data });
          }
        });
      } else {
        resolve({ ok: false, error: "chrome.identity không khả dụng" });
      }
    } catch (e) {
      resolve({ ok: false, error: e.message });
    }
  });
}

async function syncYouTubeCookies() {
  return new Promise((resolve) => {
    try {
      if (!chrome.cookies) {
        resolve({ ok: false, error: "no_cookies_permission" });
        return;
      }
      chrome.cookies.getAll({ domain: ".youtube.com" }, async (cookies) => {
        if (!cookies || cookies.length === 0) {
          resolve({ ok: false, message: "no_cookies_found" });
          return;
        }
        let netscape = "# Netscape HTTP Cookie File\n# Exported by Mallios Extension\n\n";
        for (const c of cookies) {
          const domain = c.domain.startsWith(".") ? c.domain : `.${c.domain}`;
          const flag = "TRUE";
          const path = c.path || "/";
          const secure = c.secure ? "TRUE" : "FALSE";
          const expiry = Math.floor(c.expirationDate || (Date.now() / 1000 + 86400 * 365));
          netscape += `${domain}\t${flag}\t${path}\t${secure}\t${expiry}\t${c.name}\t${c.value}\n`;
        }
        const res = await proxyApiRequest("/api/sync-cookies", {
          method: "POST",
          body: JSON.stringify({ cookies_content: netscape })
        });
        resolve({ ok: res.ok, status: res.status });
      });
    } catch (e) {
      resolve({ ok: false, error: e.message });
    }
  });
}

let lastNotificationTime = 0;
let lastNotificationMessage = "";

function showSingleNotification(title, message, priority = 2) {
  const now = Date.now();
  if (message === lastNotificationMessage && now - lastNotificationTime < 2500) {
    return;
  }
  lastNotificationTime = now;
  lastNotificationMessage = message;

  const notifId = "mallios-single-notification";
  try {
    chrome.notifications.clear(notifId, () => {
      chrome.notifications.create(notifId, {
        type: "basic",
        iconUrl: "icons/bear-icon.png",
        title: title || "Mallios MP3 Downloader",
        message: message || "Tải nhạc hoàn tất!",
        priority: priority
      });
    });
  } catch (_) {}
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "sync-cookies") {
    syncYouTubeCookies().then(sendResponse);
    return true;
  }

  if (message?.type === "check-health") {
    checkServerHealth().then(sendResponse);
    return true;
  }

  if (message?.type === "ensure-backend") {
    ensureBackendRunning().then(sendResponse);
    return true;
  }

  if (message?.type === "api-request") {
    proxyApiRequest(message.path, message.options).then(sendResponse);
    return true;
  }

  if (message?.type === "google-identity-login") {
    loginWithGoogleIdentity().then(sendResponse);
    return true;
  }

  if (message?.type === "show-notification") {
    showSingleNotification(message.title, message.message, 2);
    sendResponse({ ok: true });
    return true;
  }

  return false;
});

function broadcastToTabs(message) {
  try {
    chrome.tabs.query({}, (tabs) => {
      if (tabs && tabs.length > 0) {
        for (const tab of tabs) {
          if (tab && tab.id) {
            chrome.tabs.sendMessage(tab.id, message).catch(() => {});
          }
        }
      }
    });
  } catch (_) {}
}

chrome.runtime.onInstalled.addListener(() => {
  try {
    chrome.contextMenus.create({
      id: "mallios-download-context",
      title: "⚡ Tải MP3 bằng Mallios",
      contexts: ["link", "video", "audio", "page"]
    });
  } catch (_) {}
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "mallios-download-context") {
    const targetUrl = info.linkUrl || info.srcUrl || info.pageUrl || tab?.url;
    if (!targetUrl) return;

    showSingleNotification("⚡ Mallios MP3", "Đang tải bài hát trong nền...", 1);

    // Phát sóng sự kiện bắt đầu tải ngay tới các tab content script
    broadcastToTabs({ type: "mallios-download-started", url: targetUrl });

    try {
      // Đọc các thiết lập người dùng đã lưu từ giao diện tiện ích
      const settings = await chrome.storage.local.get([
        "yt_mp3_storage_target",
        "yt_mp3_save_path",
        "yt_mp3_quality",
        "yt_opt_no_subfolder",
        "yt_opt_loudnorm",
        "yt_opt_sponsorblock",
        "yt_opt_thumbnail"
      ]);

      const save_target = settings.yt_mp3_storage_target || "local";
      const download_path = settings.yt_mp3_save_path || "";
      const quality = settings.yt_mp3_quality || "0";
      const no_subfolder = !!settings.yt_opt_no_subfolder;
      const enable_loudnorm = !!settings.yt_opt_loudnorm;
      const enable_sponsorblock = !!settings.yt_opt_sponsorblock;
      const embed_thumbnail = !!settings.yt_opt_thumbnail;

      const res = await proxyApiRequest("/download", {
        method: "POST",
        body: JSON.stringify({
          links: [targetUrl],
          max_files: 1,
          quality: quality,
          download_path: download_path,
          save_target: save_target,
          no_subfolder: no_subfolder,
          enable_loudnorm: enable_loudnorm,
          enable_sponsorblock: enable_sponsorblock,
          embed_thumbnail: embed_thumbnail
        })
      });
      
      const data = JSON.parse(res.body || "{}");
      if (data.status === "success") {
        console.log("[Mallios Context Menu] Đã gửi lệnh tải thành công:", targetUrl);
        
        // Theo dõi tiến trình tải ngầm và gửi thông báo khi hoàn tất
        let pollCount = 0;
        const interval = setInterval(async () => {
          pollCount++;
          if (pollCount > 1200) { // Tối đa 10 phút cho video/playlist dài
            clearInterval(interval);
            return;
          }
          try {
            const progRes = await proxyApiRequest("/api/progress");
            const progData = JSON.parse(progRes.body || "{}");
            
            // Đồng bộ tiến trình liên tục tới giao diện nút nổi trên web
            broadcastToTabs({ type: "mallios-download-progress", data: progData });

            if (progData.status === "completed") {
              clearInterval(interval);
              broadcastToTabs({ type: "mallios-download-completed", data: progData });
              showSingleNotification("🎉 Mallios MP3 - Hoàn tất!", progData.message || "Đã tải bài hát thành công!", 2);
            } else if (progData.status === "failed") {
              clearInterval(interval);
              broadcastToTabs({ type: "mallios-download-failed", data: progData });
              showSingleNotification("❌ Mallios MP3 - Lỗi tải nhạc", progData.message || "Tải bài hát thất bại!", 2);
            } else if (progData.status === "cancelled") {
              clearInterval(interval);
              broadcastToTabs({ type: "mallios-download-cancelled", data: progData });
            }
          } catch (_) {}
        }, 500);
      } else {
        broadcastToTabs({ type: "mallios-download-busy", data: data });
        showSingleNotification("⚠️ Mallios MP3", data.message || "Máy chủ đang bận xử lý lượt tải khác.", 1);
      }
    } catch (e) {
      console.warn("[Mallios Context Menu] Lỗi gửi lệnh tải:", e);
    }
  }
});