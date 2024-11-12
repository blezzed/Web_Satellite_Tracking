import { selectedSatelliteName } from  './script.js'

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
const satelliteIconUrl = mapElement.dataset.satelliteIcon;
const gs_iconUrl = mapElement.getAttribute('data-gs-icon');
const latitude = parseFloat(mapElement.getAttribute('data-latitude'));
const longitude = parseFloat(mapElement.getAttribute('data-longitude'));
const name = mapElement.getAttribute('data-name');

let  overlayMaps = {};

let map = L.map('map', {
    center: [latitude, longitude],
    zoom: 6,
    minZoom: 2
});

baseMaps["OpenStreetMap"].addTo(map);

map.layersControl = L.control.layers(baseMaps, overlayMaps).addTo(map);

const colors = ['red', 'blue', 'green', 'orange', 'purple', 'yellow', 'pink', 'cyan'];
let colorIndex = 0;
let satellitePaths = {};
let satelliteMarkers = {};



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

let sat_path_socket = new WebSocket('ws://' + window.location.host + '/ws/satellite_path/');

// Function to show only the path and marker of the selected satellite
export function showSatellitePath(satelliteName) {
    // selectedSatelliteName = satelliteName;
    console.log(satelliteName);

    // Hide all paths and markers initially
    for (const name in satellitePaths) {
        satellitePaths[name].setStyle({ opacity: 0 });
    }
    for (const name in satelliteMarkers) {
        satelliteMarkers[name].setOpacity(0);
    }

    // Show only the selected satellite's path and marker
    if (satellitePaths[selectedSatelliteName]) {
        satellitePaths[selectedSatelliteName].setStyle({ opacity: 1 });
        map.fitBounds(satellitePaths[selectedSatelliteName].getBounds());
    }
    if (satelliteMarkers[selectedSatelliteName]) {
        satelliteMarkers[selectedSatelliteName].setOpacity(1);
    }
}

sat_path_socket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    // Plot each satellite's path for one orbit
    data.satellite_paths.forEach(satellite => {
        const pathCoords = satellite.path.map(coord => [coord[0], coord[1]]); // Convert lat/lon pairs

        if (satellitePaths[satellite.name]) {
            // Update the polyline with the new path
            satellitePaths[satellite.name].setLatLngs(pathCoords);
        } else {
            const pathColor = colors[colorIndex % colors.length];
            colorIndex++;

            const polyline = L.polyline(pathCoords, { color: pathColor }).addTo(map);
            satellitePaths[satellite.name] = polyline;

            map.fitBounds(polyline.getBounds());
        }

        const currentPos = pathCoords[0];
        if (satelliteMarkers[satellite.name]) {
            satelliteMarkers[satellite.name].setLatLng(currentPos);
        } else {
            const labeledIcon = createLabeledIcon(satellite.name, satelliteIconUrl);
            satelliteMarkers[satellite.name] = L.marker(currentPos, {icon: labeledIcon}).addTo(map)
                .bindPopup(`<b>${satellite.name}</b><br>Lat: ${currentPos[0].toFixed(2)}, Lon: ${currentPos[1].toFixed(2)}`);
        }
    });

    // Update visibility based on the selected satellite
    if (selectedSatelliteName) {
        showSatellitePath(selectedSatelliteName);
    }
};

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
