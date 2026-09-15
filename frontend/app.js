const sendButton = document.getElementById("sendButton");
const messageInput = document.getElementById("message");
const fileInput = document.getElementById("fileInput");
const fileInfo = document.getElementById("fileInfo");
const chatArea = document.getElementById("chatArea");

const SESSION_ID = "django-frontend-001";

function addMessage(text, type) {
    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }

    const message = document.createElement("div");
    message.className = `message ${type}`;
    message.textContent = text;

    chatArea.appendChild(message);
    chatArea.scrollTop = chatArea.scrollHeight;
}

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (!file) {
        fileInfo.textContent = "حداکثر حجم: 20MB";
        fileInfo.classList.remove("file-selected");
        return;
    }

    fileInfo.textContent = file.name;
    fileInfo.classList.add("file-selected");
});

async function sendMessage() {
    const message = messageInput.value.trim();
    const file = fileInput.files[0];

    if (!message && !file) {
        return;
    }

    if (file && file.size > 20 * 1024 * 1024) {
        addMessage("حجم فایل بیشتر از 20MB است.", "assistant");
        return;
    }

    if (message) {
        addMessage(message, "user");
    }

    sendButton.disabled = true;
    sendButton.textContent = "در حال پردازش...";

    const formData = new FormData();

    formData.append("message", message);
    formData.append("session_id", SESSION_ID);

    if (file) {
        formData.append("file", file);
    }

    try {
        const response = await fetch("/api/assistant/", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            const errorText =
                data.detail ||
                data.message ||
                "در پردازش درخواست خطایی رخ داد.";

            addMessage(errorText, "assistant");
            return;
        }

        addMessage(
            data.response || "پاسخی از Agent دریافت نشد.",
            "assistant"
        );

        messageInput.value = "";
        fileInput.value = "";
        fileInfo.textContent = "حداکثر حجم: 20MB";
        fileInfo.classList.remove("file-selected");

    } catch (error) {
        console.error(error);

        addMessage(
            "ارتباط با سرور برقرار نشد. لطفاً دوباره تلاش کنید.",
            "assistant"
        );
    } finally {
        sendButton.disabled = false;
        sendButton.innerHTML = "ارسال <span>➤</span>";
    }
}

sendButton.addEventListener("click", sendMessage);

messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});
