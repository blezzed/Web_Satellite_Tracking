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
let isUserInteracting = true;

let map = L.map('map', {
    center: [latitude, longitude],
    zoom: 6,
    minZoom: 2
});

baseMaps["Google Satellite"].addTo(map);

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

export function showSatellitePath(satelliteName) {
    console.log(satelliteName ? `Showing path for ${satelliteName}` : "Showing all satellite paths");

    if (!satelliteName) {
        // Show all paths and markers if no satellite is selected
        for (const name in satellitePaths) {
            satellitePaths[name].forEach((polyline) => polyline.setStyle({ opacity: 1 })); // Make all segments visible
        }
        for (const name in satelliteMarkers) {
            satelliteMarkers[name].setOpacity(1); // Make all markers visible
        }
        return;
    }

    // Otherwise, hide all paths and markers first
    for (const name in satellitePaths) {
        satellitePaths[name].forEach((polyline) => polyline.setStyle({ opacity: 0 })); // Hide all segments
    }
    for (const name in satelliteMarkers) {
        satelliteMarkers[name].setOpacity(0); // Hide all markers
    }

    // Show only the selected satellite's paths and marker
    if (satellitePaths[satelliteName]) {
        satellitePaths[satelliteName].forEach((polyline) => polyline.setStyle({ opacity: 1 })); // Show all path segments
        if (!isUserInteracting) {
            map.fitBounds(satellitePaths[satelliteName][0].getBounds());
        }
    }

    if (satelliteMarkers[satelliteName]) {
        // Ensure the satellite marker is visible
        const marker = satelliteMarkers[satelliteName];
        marker.setOpacity(1); // Make visible
        map.setView(marker.getLatLng(), map.getZoom(), { animate: true }); // Optionally re-center the map on the marker
    } else {
        console.warn(`No marker found for satellite: ${satelliteName}`);
    }
}

const satelliteColors = {}; // Store a fixed color for each satellite

sat_path_socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    // Plot each satellite's path for one orbit
    data.satellite_paths.forEach((satellite) => {
        const pathCoords = satellite.path.map((coord) => [coord[0], coord[1]]); // Convert lat/lon pairs

        // Split the path at the International Date Line
        const splitPaths = splitPathAtDateLine(pathCoords);

        // Assign a fixed color to the satellite if not already done
        if (!satelliteColors[satellite.name]) {
            satelliteColors[satellite.name] = colors[colorIndex % colors.length];
            colorIndex++;
        }

        const pathColor = satelliteColors[satellite.name];

        // Handle existing polyline: Remove old segments first
        if (satellitePaths[satellite.name]) {
            satellitePaths[satellite.name].forEach((polyline) => map.removeLayer(polyline));
        }

        // Draw each split segment as a separate polyline
        satellitePaths[satellite.name] = splitPaths.map((segment) => {
            const polyline = L.polyline(segment, { color: pathColor }).addTo(map);
            return polyline; // Store each polyline segment for removal later
        });

        const currentPos = pathCoords[0];
        if (satelliteMarkers[satellite.name]) {
            satelliteMarkers[satellite.name].setLatLng(currentPos);
        } else {
            const labeledIcon = createLabeledIcon(satellite.name, satelliteIconUrl);
            satelliteMarkers[satellite.name] = L.marker(currentPos, { icon: labeledIcon }).addTo(map)
                .bindPopup(`<b>${satellite.name}</b><br>Lat: ${currentPos[0].toFixed(2)}, Lon: ${currentPos[1].toFixed(2)}`);
        }
    });

    // Update visibility based on the selected satellite
    showSatellitePath(selectedSatelliteName);
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

/**
 * Splits a path into multiple segments where it crosses the International Date Line.
 *
 * @param {Array} pathCoords - List of latitude and longitude pairs [[lat, lon], [lat, lon], ...]
 * @return {Array} - Array of paths, each path being a list of lat/lon pairs
 */
function splitPathAtDateLine(pathCoords) {
    const SPLIT_THRESHOLD = 180; // Longitude limit for crossing the International Date Line
    let segments = [];
    let currentSegment = [pathCoords[0]];

    for (let i = 1; i < pathCoords.length; i++) {
        const [prevLat, prevLng] = pathCoords[i - 1];
        const [currentLat, currentLng] = pathCoords[i];

        // Check if crossing the International Date Line
        if (Math.abs(currentLng - prevLng) > SPLIT_THRESHOLD) {
            // Close the current segment and start a new one
            segments.push(currentSegment);
            currentSegment = [];
        }
        currentSegment.push([currentLat, currentLng]);
    }

    // Add the last segment
    if (currentSegment.length > 0) {
        segments.push(currentSegment);
    }

    return segments;
}

