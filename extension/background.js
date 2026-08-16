const NATIVE_HOST = "com.mallios.mp3";
const API_BASE_URL = "http://127.0.0.1:37491";

let nativePort = null;

function ensureBackendRunning() {
  return new Promise((resolve) => {
    try {
      if (!nativePort) {
        nativePort = chrome.runtime.connectNative(NATIVE_HOST);
        nativePort.onMessage.addListener((message) => {
          console.log("[Mallios] Native Host Persistent Response:", message);
        });
        nativePort.onDisconnect.addListener(() => {
          console.warn("[Mallios] Native Host Disconnected:", chrome.runtime.lastError?.message);
          nativePort = null;
        });
      }
      
      nativePort.postMessage({ command: "ensure-running" });
      
      setTimeout(() => {
          resolve({ ok: true });
      }, 1000);
      
    } catch (err) {
      console.error("[Mallios] Exception calling connectNative:", err);
      resolve({ ok: false, error: err.message });
    }
  });
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
    ensureBackendRunning();

    for (let attempt = 0; attempt < 6; attempt++) {
      await new Promise((r) => setTimeout(r, 300));
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

async function checkServerHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/status`, { method: "GET" });
    return { ok: res.ok, online: res.ok };
  } catch (_) {
    return { ok: false, online: false };
  }
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

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
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
    try {
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icons/bear-icon.png",
        title: message.title || "Mallios MP3 Downloader",
        message: message.message || "Tải nhạc hoàn tất!",
        priority: 2
      });
      sendResponse({ ok: true });
    } catch (e) {
      sendResponse({ ok: false, error: e.message });
    }
    return true;
  }

  return false;
});

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

    try {
      chrome.notifications.create("mallios-download-start", {
        type: "basic",
        iconUrl: "icons/bear-icon.png",
        title: "⚡ Mallios MP3",
        message: "Đang tải bài hát trong nền...",
        priority: 1
      });
    } catch (_) {}

    try {
      const res = await proxyApiRequest("/download", {
        method: "POST",
        body: JSON.stringify({
          links: [targetUrl],
          max_files: 1,
          quality: "0",
          download_path: "",
          save_target: "local",
          enable_loudnorm: false,
          enable_sponsorblock: false,
          embed_thumbnail: false
        })
      });
      
      const data = JSON.parse(res.body || "{}");
      if (data.status === "success") {
        console.log("[Mallios Context Menu] Đã gửi lệnh tải thành công:", targetUrl);
        
        // Theo dõi tiến trình tải ngầm và gửi thông báo khi hoàn tất
        let pollCount = 0;
        const interval = setInterval(async () => {
          pollCount++;
          if (pollCount > 120) { // Tối đa 2 phút
            clearInterval(interval);
            return;
          }
          try {
            const progRes = await proxyApiRequest("/api/progress");
            const progData = JSON.parse(progRes.body || "{}");
            if (progData.status === "completed") {
              clearInterval(interval);
              chrome.notifications.create("mallios-download-done-" + Date.now(), {
                type: "basic",
                iconUrl: "icons/bear-icon.png",
                title: "🎉 Mallios MP3 - Hoàn tất!",
                message: progData.message || "Đã tải bài hát thành công!",
                priority: 2
              });
            } else if (progData.status === "failed") {
              clearInterval(interval);
              chrome.notifications.create("mallios-download-err-" + Date.now(), {
                type: "basic",
                iconUrl: "icons/bear-icon.png",
                title: "❌ Mallios MP3 - Lỗi tải nhạc",
                message: progData.message || "Tải bài hát thất bại!",
                priority: 2
              });
            }
          } catch (_) {}
        }, 1000);
      } else {
        chrome.notifications.create("mallios-download-busy-" + Date.now(), {
          type: "basic",
          iconUrl: "icons/bear-icon.png",
          title: "⚠️ Mallios MP3",
          message: data.message || "Máy chủ đang bận xử lý lượt tải khác.",
          priority: 1
        });
      }
    } catch (e) {
      console.warn("[Mallios Context Menu] Lỗi gửi lệnh tải:", e);
    }
  }
});