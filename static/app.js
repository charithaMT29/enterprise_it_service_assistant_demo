
// =================================
// 1. Get HTML Elements
// =================================

const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const chatMessages = document.getElementById("chatMessages");
const sendButton = document.getElementById("sendButton");
const clearButton = document.getElementById("clearButton");
const typingIndicator = document.getElementById("typingIndicator");
const activityList = document.getElementById("activityList");

let conversationHistory = [];

// =================================
// 2. Display Chat Messages
// =================================

function addMessage(role, message) {
    const messageElement = document.createElement("article");

    messageElement.className = role === "user"
        ? "message user-message"
        : "message assistant-message";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = role === "user" ? "YOU" : "AI";

    const content = document.createElement("div");
    content.className = "message-content";

    const roleLabel = document.createElement("span");
    roleLabel.className = "message-role";
    roleLabel.textContent = role === "user" ? "You" : "Assistant";

    const text = document.createElement("p");
    text.textContent = message;

    content.appendChild(roleLabel);
    content.appendChild(text);

    messageElement.appendChild(avatar);
    messageElement.appendChild(content);

    chatMessages.appendChild(messageElement);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// =================================
// 3. Display Assistant Activity
// =================================

function showActivity(trace) {
    activityList.replaceChildren();

    if (!Array.isArray(trace) || trace.length === 0) {
        const item = document.createElement("li");
        item.textContent = "No tools were used for this response.";
        activityList.appendChild(item);
        return;
    }

    trace.forEach((entry) => {
        const item = document.createElement("li");

        const step = entry.step || "";
        const tool = entry.tool || entry.name || "Activity";

        item.textContent = step
            ? `Step ${step}: ${tool}`
            : tool;

        activityList.appendChild(item);
    });
}

// =================================
// 4. Format API Error Messages
// =================================

function getErrorMessage(detail) {
    if (typeof detail === "string") {
        return detail;
    }

    if (Array.isArray(detail)) {
        return detail.map((error) => {
            const location = Array.isArray(error.loc)
                ? error.loc.join(" → ")
                : "";

            return location
                ? `${location}: ${error.msg || "Invalid input"}`
                : error.msg || "Invalid input";
        }).join("; ");
    }

    if (detail && typeof detail === "object") {
        return JSON.stringify(detail);
    }

    return "The server could not process the request.";
}

// =================================
// 5. Send Message to Backend
// =================================

async function sendMessage(rawText) {
    const message = rawText.trim();

    if (!message) {
        return;
    }

    addMessage("user", message);

    sendButton.disabled = true;
    typingIndicator.hidden = false;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory.slice(-8)
            })
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                getErrorMessage(data.detail || data.error)
            );
        }

        const answer = data.answer ||
            "The assistant returned an empty response.";

        addMessage("assistant", answer);

        // Save the successful conversation.
        conversationHistory.push(
            { role: "user", content: message },
            { role: "assistant", content: answer }
        );

        // Keep only the latest eight messages.
        conversationHistory = conversationHistory.slice(-8);

        // Display the latest tool activity.
        showActivity(data.trace || data.activity || []);

    } catch (error) {
        addMessage(
            "assistant",
            `Sorry, something went wrong: ${error.message}`
        );

        // Do not leave an old activity trace visible.
        showActivity([]);

    } finally {
        sendButton.disabled = false;
        typingIndicator.hidden = true;
        messageInput.value = "";
        messageInput.focus();
    }
}

// =================================
// 6. Handle Chat Form
// =================================

chatForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const message = messageInput.value.trim();

    if (message.length < 2) {
        return;
    }

    if (message.length > 1200) {
        addMessage(
            "assistant",
            "Please keep your message within 1200 characters."
        );
        return;
    }

    sendMessage(message);
});

// =================================
// 7. Example Question Buttons
// =================================

document.querySelectorAll(".chip").forEach((button) => {
    button.addEventListener("click", () => {
        const prompt = button.dataset.prompt || "";
        sendMessage(prompt);
    });
});

// =================================
// 8. Clear Conversation
// =================================

clearButton.addEventListener("click", () => {
    conversationHistory = [];

    chatMessages.replaceChildren();
    activityList.replaceChildren();

    addMessage(
        "assistant",
        "Hello! I can help you with IT policies, assets, tickets, support teams and incident drafts. How can I help you?"
    );

    const item = document.createElement("li");
    item.textContent = "No activity yet.";

    activityList.appendChild(item);

    messageInput.focus();
});
