let baseMaps = {
    "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }),
    // Placeholder for Google Maps (Replace with compliant method)
    "Google Maps": L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        attribution: '© Google Maps'
    }),
    // Placeholder for Google Satellite (Replace with compliant method)
    "Google Satellite": L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
        attribution: '© Google Satellite'
    }),
    // Placeholder for Google Hybrid (Replace with compliant method)
    "Google Hybrid": L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        attribution: '© Google Hybrid'
    })
};

// Get references to modal, overlay, and buttons
const editButton = document.getElementById('editButton');
const editModal = document.getElementById('editModal');
const closeModal = document.getElementById('closeModal');

// Function to open the modal
function openModal() {
    editModal.style.display = 'flex';
}

// Function to close the modal
function closeModalFunction() {
    editModal.style.display = 'none';
}

// Event listeners to open and close the modal
editButton.addEventListener('click', openModal);
closeModal.addEventListener('click', closeModalFunction);

// Close modal when clicking outside the form
editModal.addEventListener('click', (event) => {
    if (event.target === editModal) {
        closeModalFunction();
    }
});

// Handle form submission with AJAX
document.getElementById('editForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(this);
    const groundStationId = this.dataset.groundstationId;

    fetch(`/ground_station/${groundStationId}/edit/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide the modal on success
            document.getElementById('editModal').classList.add('hidden');

            // Update ground station details on the page dynamically
            document.querySelector('.ground-station-name').textContent = data.ground_station.name;
            document.querySelector('.ground-station-latitude').textContent =  `(${data.ground_station.latitude}, ${data.ground_station.longitude})`;
            document.querySelector('.ground-station-altitude').textContent = data.ground_station.altitude.toFixed(1);
            document.querySelector('.ground-station-elevation').textContent = `${data.ground_station.start_tracking_elevation}°`;

            closeModalFunction();

        } else {
            // Handle errors (e.g., display error messages)
            alert("Error updating ground station.");
        }
    });
});

// Retrieve data attributes from map element
const mapElement = document.getElementById('map');
const iconUrl = mapElement.getAttribute('data-icon-url');
const latitude = parseFloat(mapElement.getAttribute('data-latitude'));
const longitude = parseFloat(mapElement.getAttribute('data-longitude'));
const name = mapElement.getAttribute('data-name');

let  overlayMaps = {};

let map = L.map('map', {
    center: [latitude, longitude],
    zoom: 6,
    minZoom: 2
});

baseMaps["Google Satellite"].addTo(map);

map.layersControl = L.control.layers(baseMaps, overlayMaps).addTo(map);


const groundStationIconWithLabel = L.divIcon({
    html: `
        <div style="text-align: center;">
            <img src="${iconUrl}" style="width: 35px; height: 35px;">
<!--            <div style="font-size: 12px; color: black; margin-top: 5px;">${name}</div>-->
        </div>
    `,
    className: '', // Remove default styling
    iconSize: [35, 45], // Adjust size to fit icon and label
    iconAnchor: [17, 35] // Adjust anchor point for proper alignment
});

// Place ground station marker with custom icon and label
const groundStationMarker = L.marker(
    [latitude, longitude],
    { icon: groundStationIconWithLabel }
).addTo(map).bindPopup(`<b>${name}</b><br>Lat: ${latitude}<br>Lon: ${longitude}`);