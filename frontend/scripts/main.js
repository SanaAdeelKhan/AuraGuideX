const userId = "aura_user001"; // static ID for demo

function addMessage(text, sender) {
  const chatLog = document.getElementById("chat-log");
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.innerText = text;
  chatLog.appendChild(msg);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  addMessage("You: " + message, "user");
  input.value = "";

  try {
    const res = await fetch("http://localhost:5000/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, user_id: userId })
    });

    const data = await res.json();
    addMessage("Aura: " + data.answer, "agent");
  } catch (err) {
    addMessage("Aura: Sorry, I'm offline or backend is unreachable.", "agent");
    console.error(err);
  }
}
