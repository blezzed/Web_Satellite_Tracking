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

export function initializeLeafletMap(mapId, latitude, longitude, trajectory = []) {
    setTimeout(() => {
        const mapElement = document.getElementById(mapId);
        if (!mapElement) {
            console.error(`Element with id ${mapId} not found.`);
            return;
        }

        // Check if the map is already initialized
        if (mapElement._leaflet_id) {
            console.log(`Map with id ${mapId} is already initialized.`);
            return;
        }

        // Initialize map
        const map = L.map(mapId, {
            center: [latitude, longitude],
            zoom: 6, // Adjust zoom level
            minZoom: 2,
        });

        // Add a base map layer
        baseMaps["Google Hybrid"].addTo(map);

        map.layersControl = L.control.layers(baseMaps).addTo(map);

        // Add marker for the MissionPlan location
        const marker = L.marker([latitude, longitude]).addTo(map);
        marker.bindPopup(`Location: (${latitude}, ${longitude})`).openPopup();

        // Draw the trajectory (as a polyline) if it exists
        if (trajectory.length > 0) {
            const polyline = L.polyline(trajectory, { color: 'blue', weight: 3 }).addTo(map);
            map.fitBounds(polyline.getBounds()); // Adjust the map to show the full trajectory
        }

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

        function calculateDistance(latlngs) {
            let totalDistance = 0;
            for (let i = 0; i < latlngs.length - 1; i++) {
                totalDistance += map.distance(latlngs[i], latlngs[i + 1]); // Use Leaflet's distance method
            }
            return totalDistance;
        }

        // Invalidate size to ensure the map renders properly
        setTimeout(() => {
            map.invalidateSize();
        }, 200);
    }, 0);
}

// Make global (if required)
window.initializeLeafletMap = initializeLeafletMap;
/*
const latitude = -17.784650;
const longitude = 31.050560;

let overlayMaps = {};

let map = L.map('map', {
    center: [latitude, longitude],
    zoom: 6,
    minZoom: 2
});

baseMaps["Google Hybrid"].addTo(map);

map.layersControl = L.control.layers(baseMaps, overlayMaps).addTo(map);

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

/!**
 * Function to calculate distance between multiple points (polyline)
 * @param {Array} latlngs - Array of LatLng points
 * @returns {number} - Total distance in meters
 *!/
function calculateDistance(latlngs) {
    let totalDistance = 0;
    for (let i = 0; i < latlngs.length - 1; i++) {
        totalDistance += map.distance(latlngs[i], latlngs[i + 1]); // Use Leaflet's distance method
    }
    return totalDistance;
}*/
