window.currentRoom = null;
let new_chat_user = null;

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
        console.log(data);

        if (data.type === "status-update") {
            const userStatusEl = document.querySelector(`#user-status-${data.user_id}`);
            if (userStatusEl) {
                if (data.online) {
                    userStatusEl.textContent = "Online";  // Show online
                } else {
                    userStatusEl.textContent = `Last Seen at 
                    ${
                        new Date(data.last_seen).toLocaleString('en-US', {
                            month: 'short',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: false
                        })
                    }
                    `; // Show last seen
                }
            } else {
                console.warn(`User status element not found for user ID: ${data.user_id}`);
            }
        }

        if (data.typing === true || data.typing === false) {
            // Update typing status dynamically
            if (data.user_id !== window.userId) {
                const roomName = `${Math.min(data.user_id, window.userId)}_${Math.max(data.user_id, window.userId)}`;
               updateTypingStatus(data.user_id, data.typing, roomName);
            }

        }

        if (data.message) {
            // Check if the message ID or temp ID already exists in the DOM
            if (document.querySelector(`[data-message-id="${data.temp_id}"]`)) {
                console.warn("Duplicate message received. Ignoring it.");
                return;
            } else {
               renderNewMessage(data);
            }

            if (data.sender !== window.userId){
                updateChatContainer(data, data.room_name);
            }

            if (data.room_name === window.currentRoom) {
                markMessagesAsRead(window.currentReceiverId);
            }
        }

        if (data.unread_count !== undefined) {
            // Update the unread message count dynamically
            updateUnreadCount(data.user_id, data.unread_count);

        }

        if (data.status) {

            const id = parseInt(data.user_id) === parseInt(window.userId) && data.status === "delivered"
                ? window.currentReceiverId
                : data.user_id;

            console.log(`User ID: ${data.user_id}`);
            console.log(`Window User ID: ${window.userId}`);
            console.log(`Is current user: ${parseInt(id) === parseInt(window.userId)}, Status is delivered: ${data.status === "delivered"}`);



            if (parseInt(data.user_id)=== parseInt(window.userId) && data.status === "delivered") {
                updateMessageStatus(data.temp_id, data.status);
                updateStatusIcon(data.status, window.currentReceiverId);
            } else if (parseInt(data.user_id) !== parseInt(window.userId) && data.status === "read") {
                updateMessageStatus(data.temp_id, data.status);
                updateStatusIcon(data.status, data.user_id);
            }

        }
    };

    socket.onclose = () => {
        console.log(`Disconnected from room: ${roomName}`);
        delete activeConnections[roomName];
    };

    // Store connection
    activeConnections[roomName] = socket;
}

function updateStatusIcon(status='sent', user_Id = window.userId) {
    const statusContainer = document.querySelector(`[data-message-receiver-id="${user_Id}"]`);

    if (!statusContainer) {
        console.warn("Cannot find space for the status tick.");
        return;
    }

    statusContainer.innerHTML = '';
    let statusIcon = document.createElement("i");
    statusIcon.id = `message-status-${window.currentReceiverId}`;
    statusIcon.className = status === "read"
        ? "fas fa-check-double text-blue-500"
        : status === "delivered"
            ? "fas fa-check-double text-grey-500"
            : "fas fa-check text-gray-500";
    statusContainer.appendChild(statusIcon);
}

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
    }
}

function updateChatContainer(data, roomName = window.currentRoom) {
    // Process incoming message and handle UI updates
    console.log(data);
    const chatListContainer = document.querySelector(".chat-list-container"); // Parent container for chat tiles
    const existingTile = document.querySelector(`[data-room-name="${roomName}"]`);
    const timestamp = new Date(data.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    if (existingTile) {
        // Update the existing tile
        const lastMessageSpan = existingTile.querySelector("#last-message-" + roomName);
        let unreadCountSpan = existingTile.querySelector(`#unread-count-${data.sender}`);
        const timestampElement = existingTile.querySelector("small");

        // Update last message
        if (lastMessageSpan) {
            lastMessageSpan.textContent = data.message;
        }

        // Update unread count
        if (data.sender !== window.userId) {
            console.log("Updating unread count for user:", data.sender, {
                sender: data.sender,
                currentUser: window.userId,
                isDifferentUser: data.sender !== window.userId,
            });
           if (unreadCountSpan) {
                unreadCountSpan.textContent = `${parseInt(unreadCountSpan.textContent || "0") + 1}`;
                unreadCountSpan.classList.remove("hidden");
            }else {
                // const statusContainer = existingTile.querySelector(`#message-status-${roomName}`);

               const statusContainer = document.querySelector(`[data-message-receiver-id="${data.sender}"]`);

                if (!statusContainer) {
                    console.warn("Cannot find space for the status tick.");
                    return;
                }

                statusContainer.innerHTML='';
                unreadCountSpan = document.createElement("span");
                unreadCountSpan.id = `unread-count-${data.sender}`;
                unreadCountSpan.className = "bg-gradient-to-bl from-rifleBlue-600 to-blue-600 text-white text-sm font-bold rounded-full h-6 w-6 flex items-center justify-center shadow-md"; // Single gray tick for sent messages
                unreadCountSpan.textContent = "1";
                statusContainer.appendChild(unreadCountSpan);
            }
        }else {
            // If the current user is the sender, ensure the unread-count span is hidden
            if (unreadCountSpan) {
                unreadCountSpan.classList.add("hidden");
            }
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
        newTile.setAttribute("data-receiver-id", sender);
        newTile.setAttribute("data-room-name", data.room_name);
        newTile.className = "px-4 py-2 border border-gray-300 rounded-xl flex items-center shadow-lg hover:border-rifleBlue-400 transition transform hover:scale-y-105 overflow-hidden";

        newTile.innerHTML = `
                <div class="w-12 h-12 bg-rifleBlue text-white rounded-full flex items-center justify-center mr-4 shadow-lg">
                    <i class="fas fa-user text-2xl"></i>
                </div>
                <div class="overflow-hidden flex-1">
                    <h6 class="font-bold text-rifleBlue-800 truncate hover:text-rifleBlue-600 transition">
                        ${data.sender===window.userId ? data.receiverName :data.senderName}</h6>
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

function addTickToSenderChat(roomName = window.currentRoom) {
    const chatTile = document.querySelector(`[data-room-name="${roomName}"]`); // Find the chat tile for the room

    if (!chatTile) {
        console.error(`Chat tile for room "${roomName}" not found.`);
        return;
    }

    // Look for the tick icon or status container
    let statusIcon = chatTile.querySelector(`#message-status-${window.currentReceiverId}`);

    if (!statusIcon) {
        // If the status icon doesn't exist, create it inside the container
        // const statusContainer = chatTile.querySelector(`#message-status-${roomName}`);
        const statusContainer = document.querySelector(`[data-message-receiver-id="${window.currentReceiverId}"]`);
        if (!statusContainer) {
            console.warn("Cannot find space for the status tick.");
            return;
        }

        statusContainer.innerHTML='';
        statusIcon = document.createElement("i");
        statusIcon.id = `message-status-${window.currentReceiverId}`;
        statusIcon.className = "fas fa-check text-gray-500"; // Single gray tick for sent messages
        statusContainer.appendChild(statusIcon);
    } else {
        // Update existing tick icon
        statusIcon.className = "fas fa-check text-gray-500";
    }
}

// Handle typing notifications
function updateTyping(isTyping, socket = activeConnections[window.currentRoom]) {
    socket.send(JSON.stringify({
        command: "typing",
        room_name: window.currentRoom,
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
function updateTypingStatus(user_id, isTyping, room_name) {
    const messagesContainer = document.getElementById(`messages-container-${room_name}`);
    const chatTileTyping = document.getElementById(`typing-status-${user_id}`);
    const lastMessageElement = document.querySelector(`[data-lst-msg-receiver-id="${user_id}"]`);

    // Debugging if elements are missing
    if (messagesContainer)  {
        let typingIndicator = document.querySelector(`#typing-indicator-${user_id}`);

        if (isTyping) {
            // If the typing indicator doesn't exist, create and append it
            if (!typingIndicator) {
                typingIndicator = document.createElement("div");
                typingIndicator.id = `typing-indicator-${user_id}`;
                typingIndicator.className = "text-sm text-gray-600 italic";
                typingIndicator.innerHTML = `
                    <p class="text-truncate text-sm text-green-500">
                        <span class="animate-typing-col font-bold text-lg">
                            <span class="dot">.</span>
                            <span class="dot">.</span>
                            <span class="dot">.</span>
                        </span>
                    </p>
                `;

                // Append the indicator at the bottom of the messages container
                messagesContainer.appendChild(typingIndicator);
            }
        } else {
            // If the user stops typing, remove the typing indicator
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }
    }

    if (!chatTileTyping || !lastMessageElement) {
        console.error("Either typing or last message element is missing for user:", userId);
        return;
    }

    // Update typing in Chat Tile
    if (isTyping === true || isTyping === "true") {
        chatTileTyping.classList.remove("hidden");
        lastMessageElement.classList.add("hidden");
    } else {
        chatTileTyping.classList.add("hidden");
        lastMessageElement.classList.remove("hidden");
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
        receiverName: new_chat_user != null? new_chat_user.username: 'Unknown',
        message: message,
        timestamp: new Date().toISOString(),
        temp_id: tempMessageId,
    };
    renderNewMessage(optimisticMessageData, true); // Pass true for optimistic rendering

    try {
        sendMessage(message, receiverId, tempMessageId); // Pass the temp ID
        updateChatContainer(optimisticMessageData);
        addTickToSenderChat();
    } catch (error) {
        console.error("Message failed to send:", error);
    }

    // Clear the input field after sending the message
    messageInput.value = "";
}

// Update the unread count dynamically
function updateUnreadCount(user_id, count) {
    const unreadCountSpan = document.getElementById(`unread-count-${user_id}`);
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
function updateMessageStatus(messageId, status) {

    if ((!messageId || messageId === '') && status === "read") {
        // Handle case when messageId is not provided
        const messagesContainer = document.getElementById(`messages-container-${window.currentRoom}`);
        if (!messagesContainer) {
            console.warn("Messages container not found for the current room.");
            return;
        }

        // Find all elements with the class 'fas fa-check-double' in the container
        const tickElements = messagesContainer.querySelectorAll(".fa-check-double");

        // Replace all gray double ticks with blue double ticks
        tickElements.forEach((tickElement) => {
            if (tickElement.classList.contains("text-gray-500")) {
                tickElement.classList.remove("text-gray-500");
                tickElement.classList.add("text-blue-500");
            }
        });

        return; // Exit as we've processed the "no messageId" case
    }

    const messageStatusElement = document.getElementById(`status-${messageId}`);

    if (!messageStatusElement) {
        console.warn(`Message status element not found for message ID: ${messageId}`);
        return;
    }

    // Clear previous icons
    messageStatusElement.innerHTML = "";
    const statusIcon = document.createElement("i");

    if (status === "read") {
        statusIcon.className = "fas fa-check-double text-blue-500"; // Blue double tick
    } else if (status === "delivered") {
        statusIcon.className = "fas fa-check-double text-gray-500"; // Gray double tick
    } else {
        statusIcon.className = "fas fa-check text-gray-500"; // Single gray tick
    }

    messageStatusElement.appendChild(statusIcon);

}

// Render a new message dynamically
function renderNewMessage(data, isOptimistic = false) {
    const chatContent = document.querySelector(`#messages-container-${window.currentRoom}`);

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

function markMessagesAsRead(receiverId) {

    console.debug("Marking messages as read for receiverId:", receiverId);
    const socket = activeConnections[window.currentRoom];
    if (socket) {
        socket.send(JSON.stringify({
            command: "mark_read",
            receiver_id: receiverId,
            sender: window.userId,
            room_name: window.currentRoom
        }));
    } else {
        console.error("WebSocket is not connected. Cannot mark messages as read.");
    }
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

                    const messagesContainer = document.getElementsByClassName('messages')[0];
                    messagesContainer.id = 'messages-container-' + window.currentRoom;

                    // Mark messages as read
                    markMessagesAsRead(receiverId);
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
    new_chat_user = user;

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
