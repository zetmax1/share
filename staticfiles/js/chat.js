
const chatbox = document.querySelector("#chatbox");
function scrollToBottom() {
  chatbox.scrollTop = chatbox.scrollHeight;
}
scrollToBottom();

const roomName = JSON.parse(document.getElementById("room_slug").textContent);
const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
const wsHost = window.location.host || "localhost:8000";
const chatSocket = new WebSocket(`${wsProtocol}${wsHost}/ws/chat/${roomName}/`);

chatSocket.onopen = function (e) {
  console.log("WebSocket connected successfully");
};
chatSocket.onerror = function (e) {
  console.error("WebSocket error:", e);
};
chatSocket.onclose = function (e) {
  console.log("WebSocket closed:", e);
};

window.onbeforeunload = function() {
  chatSocket.close();
};

document.querySelector("#my_input").focus();
document.querySelector("#my_input").onkeyup = function (e) {
  if (e.keyCode === 13) {
    e.preventDefault();
    document.querySelector("#submit_button").click();
  }
};

document.querySelector("#submit_button").onclick = function (e) {
  const messageInput = document.querySelector("#my_input").value;
  if (!messageInput) {
    alert("Please enter a message!");
    return;
  }
  console.log("Sending message:", messageInput);
  chatSocket.send(JSON.stringify({
    action: "send",
    message: messageInput
  }));
  document.querySelector("#my_input").value = "";
};

document.querySelector("#mediaInput").addEventListener("change", function (e) {
  const files = e.target.files;
  if (files.length > 0) {
    for (let file of files) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("action", "media");
      formData.append("type", file.type.startsWith("image/") ? "image" :
                             file.type.startsWith("video/") ? "video" :
                             file.type.startsWith("audio/") ? "voice" : "file");

      fetch("/upload-media/", {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": getCookie("csrftoken") }
      })
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
      })
      .then(data => {
        console.log("File uploaded:", data);
        chatSocket.send(JSON.stringify({
          action: "media",
          type: data.type,
          url: data.url,
          filename: file.name
        }));
      })
      .catch(error => {
        console.error("Error uploading file:", error);
        alert("Failed to upload file.");
      });
    }
  }
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

let mediaRecorder;
let audioChunks = [];
document.querySelector("#voiceButton").addEventListener("click", async function () {
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();
      this.innerHTML = '<i class="fas fa-stop"></i>';
      this.classList.add("recording");

      mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
      mediaRecorder.onstop = () => {
        this.classList.remove("recording");
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        audioChunks = [];

        const formData = new FormData();
        formData.append("file", audioBlob, "voice-message.webm");
        formData.append("action", "media");
        formData.append("type", "voice");

        fetch("/upload-media/", {
          method: "POST",
          body: formData,
          headers: { "X-CSRFToken": getCookie("csrftoken") }
        })
        .then(response => {
          if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
          return response.json();
        })
        .then(data => {
          chatSocket.send(JSON.stringify({
            action: "media",
            type: "voice",
            url: data.url,
            filename: "voice-message.webm"
          }));
        })
        .catch(error => {
          console.error("Error uploading voice:", error);
          alert("Failed to upload voice message.");
        });
      };
    } catch (err) {
      console.error("Microphone access error:", err);
      alert("Please allow microphone access.");
    }
  } else {
    mediaRecorder.stop();
    this.innerHTML = '<i class="fas fa-microphone"></i>';
  }
});

chatSocket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  console.log("Received WebSocket message:", data);

  if (data.action === "send" || data.action === "reply") {
    const div = document.createElement("div");
    div.id = `message-${data.message_id}`;
    div.className = `chat-message ${data.sender === "{{ request.user.username }}" ? "sender" : "receiver"}`;
    div.innerHTML = `
      <div class="message-content">
        <span>${data.message}</span>
        ${data.reply_to ? `<small>(reply to "${data.reply_to_content || ""}")</small>` : ""}
      </div>
      <div class="actions">
        <i class="fas fa-ellipsis-v" onclick="toggleDropdown('${data.message_id}')"></i>
        <div class="dropdown-menu" id="dropdown-${data.message_id}" style="display: none;">
          ${data.sender === "{{ request.user.username }}" ? `
            <div class="dropdown-item" onclick="editMessage('${data.message_id}')">Edit</div>
            <div class="dropdown-item delete" onclick="deleteMessage('${data.message_id}')">Delete</div>
          ` : ""}
          <div class="dropdown-item" onclick="replyToMessage('${data.message_id}')">Reply</div>
          <div class="dropdown-item" onclick="copyMessage('${data.message}')">Copy</div>
        </div>
      </div>
    `;
    chatbox.appendChild(div);
    scrollToBottom();
    updateSidebar(data);
  } else if (data.action === "edit") {
    const messageDiv = document.getElementById(`message-${data.message_id}`);
    if (messageDiv) {
      messageDiv.querySelector(".message-content").innerHTML = `
        <span>${data.message}</span>
        <small>(edited)</small>
        ${data.reply_to ? `<small>(reply to "${data.reply_to_content || ""}")</small>` : ""}
      `;
      scrollToBottom();
    }
  } else if (data.action === "delete") {
    const messageDiv = document.getElementById(`message-${data.message_id}`);
    if (messageDiv && data.is_deleted) {
      messageDiv.remove();
      if (!chatbox.querySelector(".chat-message")) {
        chatbox.innerHTML = '<p class="no-messages">No Messages.</p>';
      }
    }
  } else if (data.action === "media") {
    const div = document.createElement("div");
    div.id = `message-${data.message_id}`;
    div.className = `chat-message ${data.sender === "{{ request.user.username }}" ? "sender" : "receiver"}`;
    let mediaContent = "";
    if (data.type === "image") mediaContent = `<img src="${data.url}" style="max-width: 200px;" />`;
    else if (data.type === "video") mediaContent = `<video controls style="max-width: 200px;"><source src="${data.url}"></video>`;
    else if (data.type === "voice") mediaContent = `<audio controls><source src="${data.url}"></audio>`;
    else if (data.type === "file") mediaContent = `<a href="${data.url}" target="_blank">${data.filename}</a>`;
    div.innerHTML = `
      <div class="message-content">${mediaContent}</div>
      <div class="actions">
        <i class="fas fa-ellipsis-v" onclick="toggleDropdown('${data.message_id}')"></i>
        <div class="dropdown-menu" id="dropdown-${data.message_id}" style="display: none;">
          ${data.sender === "{{ request.user.username }}" ? `
            <div class="dropdown-item delete" onclick="deleteMessage('${data.message_id}')">Delete</div>
          ` : ""}
          <div class="dropdown-item" onclick="replyToMessage('${data.message_id}')">Reply</div>
        </div>
      </div>
    `;
    chatbox.appendChild(div);
    scrollToBottom();
    updateSidebar(data);
  } else if (data.type === "update_chat_list") {
    fetchUpdatedChatList();
  }
};

function toggleDropdown(messageId) {
  const dropdown = document.getElementById(`dropdown-${messageId}`);
  dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

document.addEventListener("click", function (e) {
  if (!e.target.closest(".actions i") && !e.target.closest("#searchInput") && !e.target.closest(".search-results")) {
    document.querySelectorAll(".dropdown-menu").forEach(dropdown => {
      dropdown.style.display = "none";
    });
    document.getElementById("searchResults").style.display = "none";
  }
});

function editMessage(messageId) {
  const messageDiv = document.getElementById(`message-${messageId}`);
  const currentContent = messageDiv.querySelector("span").textContent;
  const newContent = prompt("Edit message:", currentContent);
  if (newContent) {
    chatSocket.send(JSON.stringify({
      action: "edit",
      message_id: messageId,
      message: newContent
    }));
  }
}

function deleteMessage(messageId) {
  if (confirm("Are you sure you want to delete this message?")) {
    chatSocket.send(JSON.stringify({
      action: "delete_confirm",
      message_id: messageId
    }));
  }
}

function replyToMessage(messageId) {
  const content = prompt("Reply:");
  if (content) {
    chatSocket.send(JSON.stringify({
      action: "reply",
      reply_to: messageId,
      message: content
    }));
  }
}

function copyMessage(content) {
  navigator.clipboard.writeText(content).then(() => alert("Copied!"));
}

function updateSidebar(data) {
  const lastMessage = document.querySelector(".list-group-item.active #last-message");
  if (lastMessage) {
    lastMessage.innerHTML = data.sender === "{{ request.user.username }}" ? "You: " + (data.message || data.type) : (data.message || data.type);
    const timestamp = document.querySelector(".list-group-item.active .timestamp");
    const date = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    timestamp.innerHTML = date;
  }
}

function fetchUpdatedChatList() {
  fetch(window.location.pathname, {
    headers: { "X-Requested-With": "XMLHttpRequest" }
  })
  .then(response => response.json())
  .then(data => {
    const contacts = document.querySelector(".contacts");
    contacts.innerHTML = data.users.map(user => `
      <a href="/chat/${user.username}/" class="list-group-item list-group-item-action ${user.username === "{{ username }}" ? "active" : ""}">
        <div class="d-flex align-items-center">
          <img src="${user.avatar_url}" class="profile-icon rounded-circle mr-3" />
          <div class="w-100">
            <div class="d-flex justify-content-between">
              <strong class="text-truncate">${user.username}</strong>
              <small class="text-nowrap timestamp">${user.timestamp}</small>
            </div>
            <small class="d-block text-truncate last-msg" id="last-message">
              ${user.is_sender ? "You: " : ""}${user.last_message}
            </small>
          </div>
        </div>
      </a>
    `).join("");
  })
  .catch(error => console.error("Error fetching chat list:", error));
}

// Theme toggle functionality with localStorage
const themeToggle = document.getElementById("theme-toggle");
const container = document.querySelector(".container-fluid");

// Sahifa yuklanganda saqlangan temani qo‘llash
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "light";
  container.setAttribute("data-theme", savedTheme);
  themeToggle.innerHTML = savedTheme === "light" ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
});

// Tema o‘zgarganda yangi tanlovni saqlash
themeToggle.addEventListener("click", () => {
  const currentTheme = container.getAttribute("data-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  container.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  themeToggle.innerHTML = newTheme === "light" ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
});

// Search messages functionality
function searchMessages() {
  const searchInput = document.getElementById("searchInput").value.toLowerCase();
  const searchResults = document.getElementById("searchResults");
  const messages = JSON.parse(document.getElementById("chat_messages").textContent);

  if (!searchInput) {
    searchResults.style.display = "none";
    return;
  }

  const filteredMessages = messages.filter(message => 
    message.content && message.content.toLowerCase().includes(searchInput)
  );

  if (filteredMessages.length === 0) {
    searchResults.innerHTML = '<div class="search-result">No results found</div>';
  } else {
    searchResults.innerHTML = filteredMessages.map(message => `
      <div class="search-result" onclick="highlightMessage('${message.id}')">
        ${message.content}
      </div>
    `).join("");
  }
  searchResults.style.display = "block";
}

function highlightMessage(messageId) {
const messageElement = document.getElementById(`message-${messageId}`);
if (messageElement) {
    messageElement.scrollIntoView({ behavior: "smooth", block: "center" });
    messageElement.style.backgroundColor = "rgba(255, 255, 0, 0.3)";
    setTimeout(() => {
        messageElement.style.backgroundColor = "";
    }, 2000);
}
}
