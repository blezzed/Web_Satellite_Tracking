window.currentRoom = null;

const activeConnections = {}; // To store connections for multiple rooms

function connectToRoom(roomName) {
    if (activeConnections[roomName]) {
        console.log(`Already connected to room: ${roomName}`);
        return;
    }

    const socket = new WebSocket(`ws://${window.location.host}/ws/chat/${roomName}/`);

    socket.onopen = () => {
        console.log(`Connected to room: ${roomName}`);
    };

    // Listen for WebSocket messages from the server
    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.typing) {
            // Update typing status dynamically
            updateTypingStatus(data.username, data.typing);
        }

        if (data.message) {
            // Check if the message ID or temp ID already exists in the DOM
            if (document.querySelector(`[data-message-id="${data.temp_id}"]`)) {
                console.warn("Duplicate message received. Ignoring it.");
                return;
            } else {
               renderNewMessage(data);
            }
            updateChatContainer(data);
        }

        if (data.unread_count !== undefined) {
            // Update the unread message count dynamically
            updateUnreadCount(data.username, data.unread_count);
        }

        if (data.status) {
            const view = window.currentReceiverId === data.receiver_id ? "messages" : "chat";
            updateMessageStatus(data.messageId, data.status, view);
        }
    };

    socket.onclose = () => {
        console.log(`Disconnected from room: ${roomName}`);
        delete activeConnections[roomName];
    };

    // Store connection
    activeConnections[roomName] = socket;
}

// const roomName = "my_room"; // Dynamic per room
// const socket = new WebSocket(`ws://${window.location.host}/ws/chat/${roomName}/`);

function sendMessage(msg, receiverId, temp_id, socket = activeConnections[window.currentRoom]) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            command: "send_message",
            sender: window.userId,
            receiver_id: receiverId,
            message: msg,
            temp_id: temp_id,
            room_name: window.currentRoom,
        }));
    } else {
        console.error("WebSocket is not ready. Message not sent.");
        updateMessageStatus(temp_id, "failed", "messages");
    }
}

function updateChatContainer(data) {
    // Process incoming message and handle UI updates
    console.log(data);
    const chatListContainer = document.querySelector(".chat-list-container"); // Parent container for chat tiles
    const existingTile = document.querySelector(`[data-room-name="${window.currentRoom}"]`);
    const timestamp = new Date(data.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    if (existingTile) {
        // Update the existing tile
        const lastMessageSpan = existingTile.querySelector("#last-message-" + data.senderName);
        const unreadCountSpan = existingTile.querySelector(`#unread-count-${data.senderName}`);
        const timestampElement = existingTile.querySelector("small");

        // Update last message
        if (lastMessageSpan) {
            lastMessageSpan.textContent = data.message;
        }

        // Update unread count
        if (unreadCountSpan) {
            unreadCountSpan.textContent = parseInt(unreadCountSpan.textContent || "0") + 1;
            unreadCountSpan.classList.remove("hidden");
        }

        // Update timestamp
        if (timestampElement) {
            timestampElement.textContent = timestamp;
        }

        // Move the tile to the top
        chatListContainer.prepend(existingTile);
    } else {
        // Create a new tile if it doesn't exist
        const newTile = document.createElement("li");
        newTile.setAttribute("data-receiver-id", data.sender_id);
        newTile.setAttribute("data-room-name", data.room_name);
        newTile.className = "px-4 py-2 border border-gray-300 rounded-xl flex items-center shadow-lg hover:border-rifleBlue-400 transition transform hover:scale-y-105 overflow-hidden";

        newTile.innerHTML = `
                <div class="w-12 h-12 bg-rifleBlue text-white rounded-full flex items-center justify-center mr-4 shadow-lg">
                    <i class="fas fa-user text-2xl"></i>
                </div>
                <div class="overflow-hidden flex-1">
                    <h6 class="font-bold text-rifleBlue-800 truncate hover:text-rifleBlue-600 transition">
                        ${data.sender===window.userId ? '' :data.senderName}</h6>
                    <p class="text-sm text-rifleBlue-500 truncate">
                        <span id="typing-status-${data.senderName}" class="hidden text-blue-400">Typing...</span>
                        <span id="last-message-${data.senderName}" class="block truncate">${data.message}</span>
                    </p>
                </div>
                <div class="text-right space-y-1 whitespace-nowrap">
                    <small class="text-xs text-rifleBlue-600 font-semibold">${timestamp}</small>
                    <div class="flex items-center justify-end mt-1 space-x-2">
                        <span id="unread-count-${data.senderName}" class="bg-gradient-to-bl from-rifleBlue-600 to-blue-600 text-white text-sm font-bold rounded-full h-6 w-6 flex items-center justify-center shadow-md hidden">1</span>
                    </div>
                </div>
            `;

        // Add the new tile to the top of the list
        chatListContainer.prepend(newTile);
    }
}

// Handle typing notifications
function updateTyping(isTyping, socket = activeConnections[window.currentRoom]) {
    socket.send(JSON.stringify({
        command: "typing",
        user_id: window.userId,
        typing: isTyping, // Emit the typing status
    }));
}

function retrySendingMessage(messageId, socket = activeConnections[window.currentRoom]) {
    const messageElement = document.querySelector(`[data-temp-id="${messageId}"]`);
    const receiverId = window.currentReceiverId || messageElement.dataset.receiverId;
    const message = messageElement.querySelector("p").textContent;

    if (!messageElement || !receiverId) {
        console.log("Failed to locate message or receiver ID for retry");
        return;
    }

    if (socket.readyState === WebSocket.OPEN) {
        messageElement.classList.remove("bg-red-100"); // Highlight removal
        messageElement.querySelector(".retry-btn").remove(); // Remove retry button
        sendMessage(message, receiverId, messageId);
    } else {
        alert("Connection lost! Retry when connected.");
    }
}

// Update the typing status dynamically for a user
function updateTypingStatus(username, isTyping) {
    const chatTileTyping = document.getElementById(`typing-status-${username}`);
    const inChatTyping = document.getElementById("typing-indicator");

    // Update typing in Chat Tile
    if (chatTileTyping) {
        chatTileTyping.classList.toggle("hidden", !isTyping);
    }

    // Update typing inside Active Chat
    if (inChatTyping) {
        if (isTyping) {
            inChatTyping.textContent = `${username} is typing...`;
            inChatTyping.classList.remove("hidden");
        } else {
            inChatTyping.classList.add("hidden");
        }
    }
}

export function handleSendMessage(event) {
    event.preventDefault(); // Prevent the form from submitting via HTTP
    console.log("handleSendMessage triggered!");

    const messageInput = document.getElementById("message-input");
    const message = messageInput.value.trim(); // Trim whitespace
    const receiverId = window.currentReceiverId; // Handle dynamically set receiver ID

    if (!message) {
        console.warn("Message is empty. Not sent.");
        return;
    }

    if (!receiverId) {
        console.error("Receiver ID is missing. Message not sent.");
        return;
    }

    // Generate a temporary message ID for tracking
    const tempMessageId = `temp-${Date.now()}`;

    const optimisticMessageData = {
        sender: window.userId,
        receiver: receiverId,
        message: message,
        timestamp: new Date().toISOString(),
        temp_id: tempMessageId,
    };
    renderNewMessage(optimisticMessageData, true); // Pass true for optimistic rendering

    try {
        sendMessage(message, receiverId, tempMessageId); // Pass the temp ID
    } catch (error) {
        console.error("Message failed to send:", error);
        updateMessageStatus(tempMessageId, "failed", "messages"); // Mark as failed
    }

    // Clear the input field after sending the message
    messageInput.value = "";
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
function updateMessageStatus(messageId, status, view = "messages") {
    let message;

    if (view === "messages") {
        // In chat conversation
        message = document.querySelector(`[data-temp-id="${messageId}"]`);
    } else if (view === "chat") {
        // In Chat Tile
        message = document.querySelector(`#message-status-${messageId}`);
    }

    if (!message) return;

    const statusIcon = message.querySelector(".status-icon");

    if (status === "failed") {
        statusIcon.className = "fas fa-exclamation-circle text-red-500";
        const retryButton = document.createElement("button");
        retryButton.textContent = "Retry";
        retryButton.className = "retry-btn text-xs text-blue-500";

        retryButton.onclick = function () {
            retrySendingMessage(messageId);
        };

        message.appendChild(retryButton); // Add retry button
    } else {
        switch (status) {
            case "sent":
                statusIcon.className = "fas fa-check text-gray-500";
                break;
            case "delivered":
                statusIcon.className = "fas fa-check-double text-gray-500";
                break;
            case "read":
                statusIcon.className = "fas fa-check-double text-blue-500";
                break;
        }
    }
}

// Render a new message dynamically
function renderNewMessage(data, isOptimistic = false) {
    const chatContent = document.querySelector(".messages");

    if (!chatContent) {
        console.error("Chat content container not found!");
        return;
    }

    const isCurrentUser = window.userId === parseInt(data.sender);
    const timestamp = isOptimistic
        ? new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const messageHTML = `<div class="flex ${isCurrentUser ? 'justify-end mb-4 chats chats-right' : 'mb-4 chats'}" data-message-id="${data.temp_id}">
    ${isCurrentUser ? `
        <div class="chat-content">
            <div class="chat-profile-name mb-1">
                <h6 class="font-semibold text-sm text-gray-600">
                    You
                    <span class="text-xs text-gray-400 mr-2">
                        ${timestamp}
                    </span>
                </h6>
            </div>
            <div class="message-content bg-blue-500 text-white rounded-lg p-3 shadow-md">
                <p>${data.message}</p>
            </div>
            <div id="status-${data.temp_id}" class="text-xs text-gray-400">
                <i class="fas fa-check text-gray-500"></i>
            </div>
        </div>
        <div class="chat-avatar flex items-center justify-center w-10 h-10 bg-blue-500 text-white rounded-full mr-2">
            <i class="fas fa-user text-lg"></i>
        </div>
    ` : `
        <div class="chat-avatar flex items-center justify-center w-10 h-10 bg-gray-300 text-black rounded-full mr-2">
            <i class="fas fa-user text-lg"></i>
        </div>
        <div class="chat-content">
            <div class="chat-profile-name mb-1">
                <h6 class="font-semibold text-sm text-gray-600">
                    ${data.senderName || 'Unknown'}
                    <span class="text-xs text-gray-400 ml-2">
                        ${timestamp}
                    </span>
                </h6>
            </div>
            <div class="message-content bg-gray-100 text-gray-700 rounded-lg p-3 shadow-md">
                <p>${data.message}</p>
            </div>
        </div>
    `}
</div>`;

    chatContent.insertAdjacentHTML("beforeend", messageHTML);

    // Scroll to the bottom of the chat
    chatContent.scrollTop = chatContent.scrollHeight;
}

// Function to load chat messages when a room is selected
document.addEventListener("DOMContentLoaded", () => {

    function loadChatMessages(chatElement) {
        const receiverId = chatElement.getAttribute("data-receiver-id");

        if (!receiverId) {
            console.error("Receiver ID is missing!");
            return;
        }
        window.currentReceiverId = receiverId;
        window.currentRoom = receiverId > window.userId
            ? `${window.userId}_${receiverId}`
            : `${receiverId}_${window.userId}`;

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

    // Gather all room names from HTML
    function getAllRoomNames() {
        const roomElements = document.querySelectorAll("[data-room-name]");
        const roomList = [];

        roomElements.forEach((element) => {
            const roomName = element.getAttribute("data-room-name");
            if (roomName) {
                roomList.push({ name: roomName });
            }
        });

        return roomList;
    }

    // Connect to all rooms
    function joinRooms(roomList) {
        roomList.forEach((room) => {
            connectToRoom(room.name);
        });
    }

    // Initialize connections to all rooms on page load
    const roomList = getAllRoomNames(); // Fetch the list of room names
    console.log(roomList);
    joinRooms(roomList); // Connect to all room names
});

// Alpine.js component for the chat footer
function chatComponent() {
    return {
        dropdownOpen: false,
        message: '', // Bind to the input field
        typingTimeout: null,

        triggerTyping() {
            clearTimeout(this.typingTimeout);

            // Start typing
            updateTyping(true); // Using the pre-existing `updateTyping()` function

            // Stop typing after 1 second of inactivity
            this.typingTimeout = setTimeout(() => {
                updateTyping(false); // Stop typing notification
            }, 1000);
        },

        triggerSendMessage() {
            const form = document.getElementById("send-message-form");
            if (form) {
                updateTyping(false);
                // Directly call the `handleSendMessage` function attached to the form
                handleSendMessage(new Event('submit'));
            }
        },
    };
}
window.chatComponent = chatComponent;

window.selectUser = function (user) {
    console.log(`Selected user: ${user.username} (ID: ${user.id})`);
    window.currentReceiverId = user.id;
    window.currentRoom = user.id > window.userId
        ? `${window.userId}_${user.id}`
        : `${user.id}_${window.userId}`;
    connectToRoom(window.currentRoom);

    fetch(`/chat/messages/?receiver_id=${user.id}`)
        .then((response) => {
            if (response.ok) {
                return response.text(); // Parse the response as HTML
            }
            throw new Error("Failed to load chat messages.");
        })
        .then((html) => {
            const chatContent = document.getElementById("chat-content");
            const selectMessage = document.getElementById("select-chat-message");

            if (chatContent) {
                if (selectMessage) {
                    selectMessage.style.display = "none"; // Hide the default message
                }
                chatContent.innerHTML = html; // Replace chat body content
            } else {
                console.error("Chat content container not found!");
            }
        })
        .catch((error) => {
            console.error("Error loading chat messages:", error);
        });
};
