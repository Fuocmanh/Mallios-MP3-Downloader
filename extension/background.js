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

  return false;
});