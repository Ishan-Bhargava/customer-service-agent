(function () {
  const sessionId = document.body.dataset.sessionId;
  const log = document.getElementById("chat-log");
  const emptyState = document.getElementById("chat-empty");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const typingIndicator = document.getElementById("typing-indicator");
  const errorSlot = document.getElementById("chat-error-slot");

  function scrollToBottom() {
    log.scrollTop = log.scrollHeight;
  }

  function addMessage(role, text) {
    if (emptyState) emptyState.remove();
    const wrap = document.createElement("div");
    wrap.className = "msg " + role;

    const label = document.createElement("div");
    label.className = "role-label";
    label.textContent = role === "user" ? "You" : "Agent";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    wrap.appendChild(label);
    wrap.appendChild(bubble);
    log.appendChild(wrap);
    scrollToBottom();
  }

  function showError(message) {
    errorSlot.innerHTML = "";
    const el = document.createElement("div");
    el.className = "chat-error";
    el.textContent = message;
    errorSlot.appendChild(el);
  }

  function clearError() {
    errorSlot.innerHTML = "";
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    clearError();
    addMessage("user", text);
    input.value = "";
    input.disabled = true;
    typingIndicator.textContent = "Agent is typing...";

    try {
      const res = await fetch(`/api/chat/${sessionId}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();

      if (!res.ok) {
        showError(data.error || "Something went wrong. Please try again.");
      } else {
        addMessage("assistant", data.reply);
      }
    } catch (err) {
      showError("Couldn't reach the server. Check your connection and try again.");
    } finally {
      typingIndicator.textContent = "";
      input.disabled = false;
      input.focus();
    }
  });

  scrollToBottom();
})();