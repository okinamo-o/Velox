// VELOX Manifest V3 Verification Service Worker
chrome.runtime.onInstalled.addListener(() => {
  console.log("[VELOX MV3 Test Extension] Installed successfully.");
  chrome.storage.local.set({ status: "active", installed_at: Date.now() });
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "ping") {
    sendResponse({ reply: "pong", service_worker_active: true });
  }
  return true;
});
