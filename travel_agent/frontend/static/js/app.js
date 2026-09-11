// ===== STATE =====
const state = {
  history: [],        // [{role, content}]
  isLoading: false,
};

// ===== DOM REFS =====
const messagesEl    = document.getElementById("messages");
const chatForm      = document.getElementById("chatForm");
const userInput     = document.getElementById("userInput");
const sendBtn       = document.getElementById("sendBtn");
const typingEl      = document.getElementById("typingIndicator");
const welcomeCard   = document.getElementById("welcomeCard");
const suggestionsEl = document.getElementById("suggestions");
const clearBtn      = document.getElementById("clearBtn");

// ===== HELPERS =====
function timeNow() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 140) + "px";
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setLoading(val) {
  state.isLoading = val;
  sendBtn.disabled = val;
  userInput.disabled = val;
  typingEl.classList.toggle("hidden", !val);
  if (!val) scrollToBottom();
}

// ===== RENDER A MESSAGE =====
function renderMessage(role, content, isError = false) {
  // Hide welcome card on first message
  welcomeCard.classList.add("hidden");

  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "U" : "✈";

  const inner = document.createElement("div");

  const bubble = document.createElement("div");
  bubble.className = "bubble" + (isError ? " error" : "");
  bubble.textContent = content;   // safe — no innerHTML

  const time = document.createElement("div");
  time.className = "msg-time";
  time.textContent = timeNow();

  inner.appendChild(bubble);
  inner.appendChild(time);
  wrap.appendChild(avatar);
  wrap.appendChild(inner);
  messagesEl.appendChild(wrap);
  scrollToBottom();
}

// ===== SEND MESSAGE =====
async function sendMessage(text) {
  if (!text || state.isLoading) return;

  renderMessage("user", text);
  state.history.push({ role: "user", content: text });
  setLoading(true);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: state.history.slice(-12) }),
    });

    const data = await res.json();

    if (!res.ok || data.error) {
      const errMsg = data.error || `Server error ${res.status}`;
      renderMessage("bot", `⚠️ ${errMsg}`, true);
    } else {
      const reply = data.reply || "I'm sorry, I couldn't generate a response. Please try again.";
      renderMessage("bot", reply);
      state.history.push({ role: "assistant", content: reply });
    }
  } catch (err) {
    renderMessage("bot", `⚠️ Network error: ${err.message}`, true);
  } finally {
    setLoading(false);
  }
}

// ===== LOAD SUGGESTIONS =====
async function loadSuggestions() {
  try {
    const res = await fetch("/api/suggestions");
    const data = await res.json();
    (data.suggestions || []).forEach((text) => {
      const chip = document.createElement("button");
      chip.className = "suggestion-chip";
      chip.textContent = text;
      chip.type = "button";
      chip.addEventListener("click", () => {
        userInput.value = text;
        submitInput();
      });
      suggestionsEl.appendChild(chip);
    });
  } catch (_) {
    // suggestions are optional — silently ignore
  }
}

// ===== SIDEBAR CLICK HANDLERS =====
document.querySelectorAll(".dest-item, .tip-item").forEach((el) => {
  el.addEventListener("click", () => {
    const q = el.dataset.query;
    if (q) {
      userInput.value = q;
      submitInput();
    }
  });
});

// ===== CLEAR CHAT =====
clearBtn.addEventListener("click", () => {
  state.history = [];
  messagesEl.innerHTML = "";
  welcomeCard.classList.remove("hidden");
});

// ===== FORM SUBMIT =====
function submitInput() {
  const text = userInput.value.trim();
  if (!text) return;
  userInput.value = "";
  autoResize(userInput);
  sendMessage(text);
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  submitInput();
});

// Enter = send (Shift+Enter = newline)
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    submitInput();
  }
});

userInput.addEventListener("input", () => autoResize(userInput));

// ===== INIT =====
loadSuggestions();
