
export let baseMaps = {
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

const mapElement = document.getElementById("map");
const gs_iconUrl = mapElement.getAttribute('data-gs-icon');
const latitude = parseFloat(mapElement.getAttribute('data-latitude'));
const longitude = parseFloat(mapElement.getAttribute('data-longitude'));
const name = mapElement.getAttribute('data-name');

let  overlayMaps = {};

export let map = L.map('map', {
    center: [latitude, longitude],
    zoom: 6,
    minZoom: 2
});

baseMaps["Google Hybrid"].addTo(map);

map.layersControl = L.control.layers(baseMaps, overlayMaps).addTo(map);

// Define the icon using the SVG file
function createLabeledIcon(labelText, iconUrl) {
    return L.divIcon({
        html: `
            <div style="position: relative; text-align: center;">
                <img src="${iconUrl}" style="width: 35px; height: 35px;">
                <div style="position: absolute; top: 35px; font-size: 12px; color: black;">${labelText}</div>
            </div>
        `,
        className: '', // Reset any default class styling
        iconSize: [35, 45], // Icon size with space for label
        iconAnchor: [15, 15]
    });
}

const groundStationIconWithLabel = L.divIcon({
    html: `
        <div style="text-align: center;">
            <img src="${gs_iconUrl}" style="width: 35px; height: 35px;">
            <div style="font-size: 12px; color: black; margin-top: 5px;">${name}</div>
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

// Add Leaflet-Geoman toolbar
map.pm.addControls({
    position: 'topleft', // Position of tools on the map
    drawCircle: false, // Disable circle tool (not needed for measuring distances)
    drawMarker: false, // Disable the marker tool
    drawPolyline: true, // Enable the polyline tool for distance measurement
    editMode: false, // Disable edit mode
    dragMode: false, // Disable dragging of layers
    removalMode: true // Enable deleting of drawn layers
});

// Listen for the creation of a line (polyline)
map.on('pm:create', (e) => {
    if (e.shape === 'Line') {
        const layer = e.layer; // Access the created polyline layer
        const latlngs = layer.getLatLngs(); // Get coordinates of the polyline

        // Calculate and display the distance of the polyline
        const totalDistance = calculateDistance(latlngs);
        layer.bindPopup(`Total Distance: ${totalDistance.toFixed(2)} meters`).openPopup();
    }
});

map.pm.setGlobalOptions({
    templineStyle: { color: 'blue', weight: 3 },
    hintlineStyle: { color: 'blue', dashArray: [5, 5] },
    pathOptions: { color: 'red', weight: 4 }
});

// Function to calculate distance between multiple points (polyline)
function calculateDistance(latlngs) {
    let totalDistance = 0;
    for (let i = 0; i < latlngs.length - 1; i++) {
        totalDistance += map.distance(latlngs[i], latlngs[i + 1]); // Use Leaflet's distance method
    }
    return totalDistance;
}




