
import { map } from './leaflet.js'; // Import existing initialized map

const input = document.getElementById("locationSearch");
const suggestionsBox = document.getElementById("suggestions");

// Function to fetch suggestions from the Nominatim API
async function fetchSuggestions(query) {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&addressdetails=1&limit=5`;
    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch suggestions");
    return await response.json();
}

// Debounce function to optimize API calls
function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Event listener for user input
input.addEventListener("input", debounce(async (e) => {
    const query = e.target.value.trim();
    console.log(query);
    if (query.length < 2) {
        suggestionsBox.classList.add("hidden"); // Hide dropdown if query is too short
        return;
    }

    try {
        const suggestions = await fetchSuggestions(query);
        console.log(suggestions);
        // Clear previous suggestions
        suggestionsBox.innerHTML = "";

        if (suggestions.length > 0) {
            suggestions.forEach((location) => {
                const suggestionItem = document.createElement("div");
                suggestionItem.textContent = location.display_name;
                suggestionItem.className = "p-2 cursor-pointer hover:bg-gray-200";

                // Handle click event on a suggestion
                suggestionItem.addEventListener("click", () => {
                    const { lat, lon, display_name } = location;

                    // Zoom the Leaflet map to the selected location
                    map.setView([parseFloat(lat), parseFloat(lon)], 12);

                    // Add a marker at the selected location
                    L.marker([parseFloat(lat), parseFloat(lon)])
                        .addTo(map)
                        .bindPopup(`<strong>${display_name}</strong>`)
                        .openPopup();

                    // Set the input value to the selected location name
                    input.value = display_name;

                    // Hide the suggestions dropdown
                    suggestionsBox.classList.add("hidden");
                });

                // Append suggestion item to the dropdown
                suggestionsBox.appendChild(suggestionItem);
            });

            suggestionsBox.classList.remove("hidden");
        } else {
            suggestionsBox.classList.add("hidden"); // Hide dropdown if no results
        }
    } catch (error) {
        console.error("Error fetching suggestions:", error);
        suggestionsBox.classList.add("hidden"); // Hide dropdown on error
    }
}, 300)); // 300ms debounce delay

// Hide suggestions dropdown when clicking outside the input
document.addEventListener("click", (e) => {
    if (!e.target.closest("#locationSearch") && !e.target.closest("#suggestions")) {
        suggestionsBox.classList.add("hidden");
    }
});

















// Calculate satellite position on the radar
function calculatePosition(azimuth, elevation) {
    const maxRadius = 200; // Outer edge of radar is 0° elevation
    const radius = maxRadius * (90 - elevation) / 90; // Map elevation to radius

    const theta = azimuth * (Math.PI / 180); // Convert azimuth to radians
    const x = radius * Math.sin(theta); // X is based on sine of angle
    const y = -radius * Math.cos(theta); // Y is based on cosine (negative for correct axis)

    return { x, y };
}

function updateSatellite(azimuth, elevation) {
    // Calculate cartesian position
    const position = calculatePosition(azimuth, elevation);

    // Update the satellite marker
    const satelliteMarker = document.getElementById('satellite-marker');
    satelliteMarker.setAttribute('cx', position.x);
    satelliteMarker.setAttribute('cy', position.y);
}

// Simulate updates in real-time
/*setInterval(() => {
    // Fetch azimuth, elevation from backend API
    fetch('/api/satellite-info')
        .then(response => response.json())
        .then(data => {
            const { azimuth, elevation } = data; // Get azimuth/elevation
            updateSatellite(azimuth, elevation); // Move the satellite on radar
        });
}, 1000); // Update every second*/

const trail = []; // Previous positions

function updateTrail(position) {
    // Add the current position to the trail
    trail.push(position);

    // Limit trail length
    if (trail.length > 10) trail.shift(); // Only 10 points in the trail

    // Draw trail positions
    const radar = document.getElementById('radar');
    radar.innerHTML = trail.map((pos, index) =>
        `<circle cx="${pos.x}" cy="${pos.y}" r="${5 - index * 0.5}" fill="rgba(255,0,0,${1 - index * 0.1})"></circle>`
    ).join('');
}