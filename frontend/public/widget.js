/**
 * Sceptre Estate AI Chat Widget — Embeddable Script
 *
 * Usage:
 *   <script src="https://your-domain.com/widget.js"
 *           data-api-base="https://api.your-domain.com"
 *           data-agent-name="Layla"
 *           data-primary-color="#2563eb">
 *   </script>
 */
(function () {
  "use strict";

  const script = document.currentScript || document.querySelector('script[data-api-base]');
  const API_BASE = script?.getAttribute("data-api-base") || "";
  const AGENT_NAME = script?.getAttribute("data-agent-name") || "Layla";
  const PRIMARY = script?.getAttribute("data-primary-color") || "#2563eb";
  const GREETING = script?.getAttribute("data-greeting") || `Hello! I'm ${AGENT_NAME}, your Dubai real estate specialist. How can I help you today?`;

  let convId = null;
  let open = false;
  let messages = [{ role: "assistant", content: GREETING }];
  let loading = false;

  // Inject styles
  const style = document.createElement("style");
  style.textContent = `
    #rea-widget * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    #rea-widget-fab {
      position: fixed; bottom: 20px; right: 20px; z-index: 9999;
      width: 56px; height: 56px; border-radius: 50%;
      background: ${PRIMARY}; color: #fff; border: none; cursor: pointer;
      box-shadow: 0 4px 20px rgba(0,0,0,0.2);
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s;
    }
    #rea-widget-fab:hover { transform: scale(1.05); }
    #rea-widget-panel {
      position: fixed; bottom: 88px; right: 20px; z-index: 9998;
      width: 360px; height: 500px; border-radius: 16px;
      background: #fff; box-shadow: 0 8px 40px rgba(0,0,0,0.18);
      border: 1px solid #e5e7eb; display: flex; flex-direction: column;
      transition: opacity 0.2s, transform 0.2s;
      overflow: hidden;
    }
    #rea-widget-panel.hidden { opacity: 0; pointer-events: none; transform: translateY(12px); }
    #rea-widget-header {
      background: ${PRIMARY}; color: #fff; padding: 12px 16px;
      display: flex; align-items: center; gap: 10px; flex-shrink: 0;
    }
    #rea-widget-header .avatar {
      width: 32px; height: 32px; border-radius: 50%;
      background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center;
    }
    #rea-widget-header .name { font-weight: 600; font-size: 14px; }
    #rea-widget-header .sub { font-size: 11px; opacity: 0.8; }
    #rea-widget-messages {
      flex: 1; overflow-y: auto; padding: 12px; background: #f9fafb;
      display: flex; flex-direction: column; gap: 10px;
    }
    .rea-msg { display: flex; gap: 8px; align-items: flex-end; }
    .rea-msg.user { flex-direction: row-reverse; }
    .rea-bubble {
      max-width: 78%; padding: 8px 12px; border-radius: 14px;
      font-size: 13px; line-height: 1.5;
    }
    .rea-msg.user .rea-bubble { background: ${PRIMARY}; color: #fff; border-bottom-right-radius: 4px; }
    .rea-msg.assistant .rea-bubble {
      background: #fff; border: 1px solid #e5e7eb; color: #111;
      border-bottom-left-radius: 4px;
    }
    .rea-dots span {
      display: inline-block; width: 6px; height: 6px; border-radius: 50%;
      background: #9ca3af; margin: 0 1px;
      animation: rea-bounce 0.9s infinite ease-in-out;
    }
    .rea-dots span:nth-child(2) { animation-delay: 0.15s; }
    .rea-dots span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes rea-bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-6px)} }
    #rea-widget-input-area {
      padding: 10px 12px; background: #fff; border-top: 1px solid #f0f0f0; flex-shrink: 0;
    }
    #rea-widget-input-row { display: flex; gap: 8px; align-items: flex-end; }
    #rea-widget-input {
      flex: 1; border: 1px solid #d1d5db; border-radius: 12px;
      padding: 8px 12px; font-size: 13px; resize: none; max-height: 80px;
      outline: none; font-family: inherit;
    }
    #rea-widget-input:focus { border-color: ${PRIMARY}; box-shadow: 0 0 0 2px ${PRIMARY}22; }
    #rea-widget-send {
      padding: 8px; background: ${PRIMARY}; color: #fff; border: none; border-radius: 10px;
      cursor: pointer; flex-shrink: 0; transition: opacity 0.2s;
    }
    #rea-widget-send:disabled { opacity: 0.4; cursor: default; }
    #rea-widget-footer { text-align: center; font-size: 10px; color: #d1d5db; margin-top: 4px; }
  `;
  document.head.appendChild(style);

  // Build DOM
  const root = document.createElement("div");
  root.id = "rea-widget";

  root.innerHTML = `
    <div id="rea-widget-panel" class="hidden">
      <div id="rea-widget-header">
        <div class="avatar">
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-3 3v-3z"/>
          </svg>
        </div>
        <div>
          <div class="name">${AGENT_NAME}</div>
          <div class="sub">Dubai Real Estate Specialist</div>
        </div>
      </div>
      <div id="rea-widget-messages"></div>
      <div id="rea-widget-input-area">
        <div id="rea-widget-input-row">
          <textarea id="rea-widget-input" rows="1"
            placeholder="Ask about properties in Dubai…"></textarea>
          <button id="rea-widget-send" disabled>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
            </svg>
          </button>
        </div>
        <div id="rea-widget-footer">Powered by Sceptre Estate AI</div>
      </div>
    </div>
    <button id="rea-widget-fab" aria-label="Open chat">
      <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-3 3v-3z"/>
      </svg>
    </button>
  `;
  document.body.appendChild(root);

  const panel = root.querySelector("#rea-widget-panel");
  const fab = root.querySelector("#rea-widget-fab");
  const messagesEl = root.querySelector("#rea-widget-messages");
  const inputEl = root.querySelector("#rea-widget-input");
  const sendBtn = root.querySelector("#rea-widget-send");

  function renderMessages() {
    messagesEl.innerHTML = "";
    messages.forEach((m) => {
      const row = document.createElement("div");
      row.className = `rea-msg ${m.role}`;
      row.innerHTML = `<div class="rea-bubble">${m.content}</div>`;
      messagesEl.appendChild(row);
    });
    if (loading) {
      const row = document.createElement("div");
      row.className = "rea-msg assistant";
      row.innerHTML = `<div class="rea-bubble"><span class="rea-dots"><span></span><span></span><span></span></span></div>`;
      messagesEl.appendChild(row);
    }
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function ensureConversation() {
    if (convId) return convId;
    const res = await fetch(`${API_BASE}/api/v1/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ channel: "web", language: "en" }),
    });
    if (!res.ok) throw new Error("conversation_create_failed");
    const data = await res.json();
    convId = data.id;
    return convId;
  }

  async function send() {
    const text = (inputEl.value || "").trim();
    if (!text || loading) return;
    inputEl.value = "";
    sendBtn.disabled = true;
    messages.push({ role: "user", content: text });
    loading = true;
    renderMessages();

    try {
      const cid = await ensureConversation();
      const res = await fetch(`${API_BASE}/api/v1/conversations/${cid}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text, language: "en", attachments: [] }),
      });
      if (!res.ok) throw new Error("send_failed");
      const data = await res.json();
      messages.push({ role: "assistant", content: data.content });
    } catch {
      messages.push({ role: "assistant", content: "I'm having a moment. Please try again." });
    } finally {
      loading = false;
      renderMessages();
    }
  }

  fab.addEventListener("click", () => {
    open = !open;
    panel.classList.toggle("hidden", !open);
    if (open) { renderMessages(); inputEl.focus(); }
  });

  inputEl.addEventListener("input", () => {
    sendBtn.disabled = !inputEl.value.trim();
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 80) + "px";
  });

  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  });

  sendBtn.addEventListener("click", send);

  renderMessages();
})();
