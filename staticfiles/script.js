
// Select all navigation items
const navItems = document.querySelectorAll('.nav-item');

navItems.forEach(item => {
  item.addEventListener('click', () => {
    // Remove 'active' class from all items
    navItems.forEach(i => i.classList.remove('active'));

    // Add 'active' class to the clicked item
    item.classList.add('active');

    // Navigate to the URL specified in the data-url attribute
    const url = item.getAttribute('data-url');
    if (url) {
      window.location.href = url;
    }
  });
});

const socket = new WebSocket('ws://' + window.location.host + "/ws/telemetry/");

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log("New Telemetry Data:", data);

    // Show a notification tile
    showNotification("New Telemetry Data Received", JSON.stringify(data));
};

socket.onclose = function (event) {
    console.error("WebSocket closed unexpectedly");
};

// Function to show a notification tile
function showNotification(title, message) {
    const container = document.getElementById('notification-container');

    // Create a notification tile
    const tile = document.createElement('div');
    tile.className = `
        bg-green-500 text-white px-4 py-3 rounded-lg shadow-lg
        transform transition-opacity duration-500 ease-out
    `;
    tile.innerHTML = `
        <div class="font-bold">${title}</div>
        <div class="text-sm">${message}</div>
    `;

    // Add the tile to the container
    container.appendChild(tile);

    // Remove the tile after 5 seconds with a fade-out effect
    setTimeout(() => {
        tile.classList.add('opacity-0');
        setTimeout(() => container.removeChild(tile), 500); // Remove from DOM after fade-out
    }, 5000);
}

