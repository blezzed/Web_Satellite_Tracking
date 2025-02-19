const roomName = "my_room"; // Dynamic per room
const socket = new WebSocket(`ws://${window.location.host}/ws/chat/${roomName}/`);

// When the socket connects
socket.onopen = function (event) {
    console.log("WebSocket connected.");
};

// Listen for WebSocket messages from the server
socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    if (data.typing) {
        // Update typing status dynamically
        updateTypingStatus(data.username, data.typing);
    }

    if (data.message) {
        // Update the chat list with the new message
        renderNewMessage(data);
    }

    if (data.unread_count !== undefined) {
        // Update the unread message count dynamically
        updateUnreadCount(data.username, data.unread_count);
    }

    if (data.status) {
        // Update message status (sent/delivered/read)
        updateMessageStatus(data.username, data.status);
    }
};

// Send a message through the WebSocket
function sendMessage(msg, receiverId) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            command: "send_message",
            sender: window.userId, // User ID from Django (or set globally)
            receiver_id: receiverId,
            message: msg,
        }));
    } else {
        console.error("WebSocket is not ready. Message not sent.");
    }
}
window.sendMessage = sendMessage;

// Handle typing notifications
function updateTyping() {
    socket.send(JSON.stringify({
        command: "typing",
        user_id: window.userId, // Update typing status for this user
    }));
}

// Update the typing status dynamically for a user
function updateTypingStatus(username, isTyping) {
    const typingSpan = document.getElementById(`typing-status-${username}`);
    if (typingSpan) {
        typingSpan.classList.toggle("hidden", !isTyping); // Show/Hide based on isTyping
    }
}

// Update the last message dynamically
function updateLastMessage(username, message) {
    const lastMessageSpan = document.getElementById(`last-message-${username}`);
    if (lastMessageSpan) {
        lastMessageSpan.textContent = message;
    }
}

// Update the unread count dynamically
function updateUnreadCount(username, count) {
    const unreadCountSpan = document.getElementById(`unread-count-${username}`);
    if (unreadCountSpan) {
        if (count > 0) {
            unreadCountSpan.textContent = count;
            unreadCountSpan.classList.remove("hidden"); // Show badge if count > 0
        } else {
            unreadCountSpan.classList.add("hidden"); // Hide badge if count is 0
        }
    }
}

// Update the message status dynamically
function updateMessageStatus(username, status) {
    const statusIcon = document.getElementById(`message-status-${username}`);
    if (!statusIcon) return;

    if (status === "read") {
        statusIcon.className = "fas fa-check-double text-blue-500";
    } else if (status === "delivered") {
        statusIcon.className = "fas fa-check-double";
    } else if (status === "sent") {
        statusIcon.className = "fas fa-check";
    }
}

// Render a new message dynamically
function renderNewMessage(data) {
    const chatContent = document.querySelector(".flex-grow.flex.flex-col .space-y-6");
    if (!chatContent) {
        console.error("Chat content container not found!");
        return;
    }

    // Ensure user ID and sender are logged for debugging
    console.log("Dynamic message render:", data);

    const isCurrentUser = window.userId === parseInt(data.sender); // Ensure user ID comparison is correct

    let formattedTimestamp = "Unknown Time";
    try {
        const date = new Date(data.timestamp);
        if (!isNaN(date.getTime())) { // Check for valid date
            formattedTimestamp = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else {
            console.error("Invalid date format:", data.timestamp);
        }
    } catch (e) {
        console.error("Error while parsing timestamp:", e);
    }

    // Create the message HTML
    const messageHTML = `<div class="flex ${isCurrentUser ? 'justify-end' : ''}">
    ${isCurrentUser ? `
        <div class="bg-rifleBlue-600 text-white rounded-xl p-4 shadow-md">
            <h6 class="font-bold">You</h6>
            <p>${data.message}</p>
            <small class="text-xs text-gray-200 float-right">${formattedTimestamp}</small>
        </div>
    ` : `
        <div class="w-10 h-10 bg-indigo-500 text-white rounded-full flex items-center justify-center mr-4">
            <i class="fas fa-user text-2lg"></i>
        </div>
        <div class="bg-rifleBlue-100 rounded-xl p-4 shadow-md">
            <p class="text-gray-700">${data.message}</p>
            <small class="text-xs text-gray-500 float-right">${formattedTimestamp}</small>
        </div>
    `}
</div>
`;

    chatContent.insertAdjacentHTML("beforeend", messageHTML);
}
// Handle message sending
function handleSendMessage(msg, receiverId) {
    const message = msg;

    if (!message) {
        console.warn("Message is empty, not sent.");
        return;
    }

    if (!receiverId) {
        console.error("Receiver ID is missing!");
        return;
    }

    // Optimistic rendering
    const temporaryMessageData = {
        sender: window.userId, // Current user ID
        message: message,      // Message text
        timestamp: new Date().toISOString(), // Current timestamp
    };
    // renderNewMessage(temporaryMessageData); // Optimistically show the message

    // Send message via WebSocket
    sendMessage(message, receiverId);

}
window.handleSendMessage = handleSendMessage;

// Function to load chat messages when a room is selected
document.addEventListener("DOMContentLoaded", () => {
    function loadChatMessages(chatElement) {
        const receiverId = chatElement.getAttribute("data-receiver-id");

        if (!receiverId) {
            console.error("Receiver ID is missing!");
            return;
        }

        fetch(`/chat/messages/?receiver_id=${receiverId}`)
            .then((response) => {
                if (response.ok) {
                    return response.text();
                }
                throw new Error("Failed to load chat messages.");
            })
            .then((html) => {
                const chatContent = document.getElementById('chat-content');
                const selectMessage = document.getElementById('select-chat-message');

                if (chatContent) {
                    if (selectMessage) {
                        selectMessage.style.display = 'none';
                    }
                    chatContent.innerHTML = html;
                } else {
                    console.error("Chat content container not found!");
                }
            })
            .catch((error) => {
                console.error("Error loading chat messages:", error);
            });
    }

    // Example event listener for chat list clicks
    document.querySelectorAll("[data-receiver-id]").forEach((chatElement) => {
        chatElement.addEventListener("click", () => {
            loadChatMessages(chatElement);
        });
    });
});