import {map} from './leaflet.js'; // Import existing initialized map


let longPressTimeout; // Used for detecting long presses
let currentMarker; // To store the reference of the latest created marker

// Listen for long press on the map
map.on('mousedown', (e) => {
    // Start a timeout when the mouse is pressed down for a long press
    longPressTimeout = setTimeout(() => {
        // This will trigger after 800ms (indicating a "long press")
        createMarkerAtLocation(e.latlng);
    }, 800); // Customize long-press delay if needed
});

// Clear the timeout if the mouse is released too quickly
map.on('mouseup', () => {
    clearTimeout(longPressTimeout);
});

// Function to create or update a marker at the picked location
function createMarkerAtLocation(latlng) {
    const { lat, lng } = latlng;

    // If a marker already exists, remove it first
    if (currentMarker) {
        map.removeLayer(currentMarker);
    }

    // Add a new marker at the picked location
    currentMarker = L.marker([lat, lng]).addTo(map);
    currentMarker.bindPopup(`Latitude: ${lat.toFixed(6)}<br>Longitude: ${lng.toFixed(6)}`).openPopup();

    // Update the sidebar inputs and h2 tag with the new location
    updateSidebar(lat, lng);
}

// Function to update the sidebar with the picked location
function updateSidebar(lat, lng) {
    // Get the input fields and the h2 tag
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');
    const locationHeader = document.querySelector('#picked-location h2');

    // Update their values/content
    latitudeInput.value = lat.toFixed(6); // Round to 6 decimal places
    longitudeInput.value = lng.toFixed(6);
    locationHeader.textContent = 'Picked location';
}


const input = document.getElementById("locationSearch"); // Input field for user location search
const suggestionsBox = document.getElementById("suggestions"); // Container for suggestions dropdown

$('#orbiting-satellites').select2({ // Initialize Select2 library on the satellite dropdown
    placeholder: 'Select an orbiting satellite', // Placeholder text for clarity
    allowClear: true,
    width: '100%',
    dropdownParent: $('.fixed.inset-0')
}).on('select2:select', function (e) {
     // Get the selected value
    missionPlanSidebar.$data.configuration.orbitingSatellite = $(this).val(); // Sync with Alpine.js
}).on('select2:unselect', function () {
    missionPlanSidebar.$data.configuration.orbitingSatellite = null; // Clear the value
});

// Fetch location suggestions from the Nominatim API based on user query
async function fetchSuggestions(query) {
    // const apiKey = "AIzaSyC9m4LohJQ50CHYCTDcht8E-A5fWwdO5xg";
    // const url = `https://maps.googleapis.com/maps/api/place/autocomplete/json?input=${encodeURIComponent(query)}&key=${apiKey}`;
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&addressdetails=1&limit=5`;
    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch suggestions");
    return await response.json();
}

// Debounce utility function to optimize and limit API call frequency
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
    if (query.length < 2) { // Ignore input too short for meaningful suggestions
        suggestionsBox.classList.add("hidden"); // Hide suggestions dropdown
        return;
    }

    try {
        const suggestions = await fetchSuggestions(query); // Fetch suggestions from the API
        console.log(suggestions); // Debug fetched suggestions
        // Clear previous suggestions to avoid duplication
        suggestionsBox.innerHTML = "";

        if (suggestions.length > 0) {
            suggestions.forEach((location) => {
                const suggestionItem = document.createElement("div");
                suggestionItem.textContent = location.display_name;
                suggestionItem.className = "p-2 cursor-pointer hover:bg-gray-200";

                // Add click listener to update map and input field on selecting a suggestion
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
                    input.value = display_name; // Update input field to show selected location
                    // Hide suggestions once a location is selected
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
    } catch (error) { // Handle network errors or API failures
        console.error("Error fetching suggestions:", error); // Log error for debugging
        suggestionsBox.classList.add("hidden"); // Hide dropdown on error
    }
}, 300)); // 300ms debounce delay

// Hide suggestions dropdown when clicking outside the input
document.addEventListener("click", (e) => { // Hide suggestions when clicking outside the input or dropdown
    if (!e.target.closest("#locationSearch") && !e.target.closest("#suggestions")) { // Check if click is outside
        suggestionsBox.classList.add("hidden");
    }
});

const satelliteSelect = document.querySelector("#orbiting-satellites");
const predictionButton = document.querySelector(".pass-prediction-button");

function toggleButton() {
    console.log("Selected satellite:", satelliteSelect.value); // Log currently selected satellite
    predictionButton.disabled = !satelliteSelect.value; // Disable button if no satellite is selected
}

// For native <select> or if select2 is NOT being used
satelliteSelect.addEventListener("change", toggleButton);

// For select2-enabled <select>
$(satelliteSelect).on("select2:select", toggleButton);
$(satelliteSelect).on("select2:unselect", toggleButton);

// Initial check to disable the button (so it aligns with the state on page load)
toggleButton();

document.querySelector("button.pass-prediction-button")
    .addEventListener("click", async () => {
        // Collect values from the frontend inputs
        const latitude = document.getElementById("latitude").value;
        const longitude = document.getElementById("longitude").value;
        const satelliteId = document.getElementById("orbiting-satellites").value;
        const minElevation = document.getElementById("min-elevation").value;
        const predictionDays = document.getElementById("prediction-days").value;
        const sunIllumination = document.getElementById("sun-illumination").checked;

        // Validate required inputs
        if (!latitude || !longitude || !satelliteId) { // Validate critical inputs are provided
            alert("Please provide latitude, longitude, and select a satellite."); // Notify user of missing fields
            return;
        }

        try {
            // Send a POST request to the backend
            const response = await fetch("/api/predict-passes/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}",
                },
                body: JSON.stringify({
                    latitude,
                    longitude,
                    satellite_id: satelliteId,
                    min_elevation: minElevation,
                    prediction_days: predictionDays,
                    sun_illumination: sunIllumination,
                }),
            });

            // Handle the response from the backend
            if (!response.ok) throw new Error("Failed to fetch satellite pass predictions.");

            const result = await response.json();

            // Locate the container element for pass results
            const container = document.getElementById("pass-prediction-container"); // Clear content before appending new results
            container.innerHTML = ""; // Clear previous results

            if (result.passes && result.passes.length > 0) {
                result.passes.forEach((satellitePass) => { // Loop through available passes
                    // Generate UI for each pass prediction with relevant details
                    const passDiv = document.createElement("div");
                    passDiv.classList.add("pass-prediction-tile");

                    // Populate the div with pass details
                    passDiv.innerHTML = `
                        <strong>Rise Time:</strong> ${satellitePass.rise_time || "N/A"}<br>
                        <strong>Set Time:</strong> ${satellitePass.set_time || "N/A"}<br>
                        <strong>Max Elevation:</strong> ${satellitePass.max_elevation || "N/A"}°<br>
                        <strong>Max Azimuth:</strong> ${satellitePass.max_azimuth || "N/A"}°<br>
                        <strong>Distance at Max Point:</strong> ${satellitePass.distance || "N/A"} km<br>
                    `;

                    // Insert generated pass details into the predictions container
                    container.appendChild(passDiv); // Append to the parent container
                });
            } else {
                // Display a message if no passes are found
                container.innerHTML = `
                    <div class="h-full w-full flex flex-col items-center justify-center">
                        <p class='text-gray-600'>No passes found for the selected parameters.</p>
                    </div>
                `;
            }
        } catch (error) { // Handle errors during pass prediction retrieval
            console.error("Error fetching satellite passes:", error); // Log error for diagnostics
            alert("There was an error fetching the satellite passes. Please try again.");
        }
    });

// Select the container and the "Calculate trajectory" button
const passPredictionContainer = document.getElementById("pass-prediction-container");
const calculateTrajectoryButton = document.querySelector(".calculate-trajectory-button");

// Alpine.js: expose `mission_plan_sidebar` x-data
const missionPlanSidebar = document.querySelector("#mission_plan_sidebar").__x;

// Add click event listeners to each pass tile
passPredictionContainer.addEventListener("click", (e) => {
    const passTile = e.target.closest(".pass-prediction-tile");
    if (!passTile) return; // Ensure only tiles trigger this logic

    // Remove the active class from all other tiles
    document
        .querySelectorAll(".pass-prediction-tile")
        .forEach(tile => tile.classList.remove("active-pass-prediction-tile"));

    // Add the active class to the selected tile
    passTile.classList.add("active-pass-prediction-tile");
    // Add active styles to the selected prediction card
    // Extract pass details for trajectory calculation
    // Update mission_plan_sidebar's x-data with selected pass details
    missionPlanSidebar.$data.selectedPass = {
        riseTime: passTile.querySelector('strong:nth-of-type(1)').nextSibling.textContent.trim(),
        setTime: passTile.querySelector('strong:nth-of-type(2)').nextSibling.textContent.trim(),
        maxElevation: passTile.querySelector('strong:nth-of-type(3)').nextSibling.textContent.trim(),
        maxAzimuth: passTile.querySelector('strong:nth-of-type(4)').nextSibling.textContent.trim(),
        distance: passTile.querySelector('strong:nth-of-type(5)').nextSibling.textContent.trim()
    };

    // Enable the "Calculate trajectory" button
    calculateTrajectoryButton.disabled = false;
});


// On "Calculate trajectory" button click
document.querySelector(".calculate-trajectory-button").addEventListener("click", async () => {
    const { selectedPass, configuration, latitude, longitude } = missionPlanSidebar.$data; // Sync sidebar state
    // Check critical conditions before proceeding with trajectory calculation
    if (!selectedPass) {
        alert("No pass selected. Please select a pass and try again.");
        return;
    }

    console.log("Satellite ID:", configuration.orbitingSatellite);

    if (!configuration.orbitingSatellite) {
        alert("No satellite selected. Please select a satellite and try again.");
        return;
    }



    try {
        // Step 1: Calculate trajectory (fetch path data)
        const response = await fetch("/api/calculate_trajectory/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": "{{ csrf_token }}", // Replace with appropriate CSRF handling
            },
            body: JSON.stringify({
                riseTime: selectedPass.riseTime,
                setTime: selectedPass.setTime,
                satellite: configuration.orbitingSatellite, // Selected Satellite ID
            }),
        });

        if (!response.ok) throw new Error("Trajectory calculation failed.");

        const result = await response.json();
        const trajectory = result.trajectory; // Coordinates array for the trajectory path [[lat, lng], ...]

        if (!trajectory || trajectory.length === 0) { // Check if trajectory data exists
            alert("No trajectory data available for the selected pass."); // Notify if data is unavailable
            return;
        }

        // Step 2: Save trajectory in x-data and close modal
        missionPlanSidebar.$data.openPlanModal = false; // Close modal
        missionPlanSidebar.$data.trajectory = trajectory; // Store trajectory for later use

        // Step 3: Clear existing markers and add the location marker
        clearMapMarkers(); // Function to clear markers (see below)
        const initialPosition = [parseFloat(latitude), parseFloat(longitude)];
        const locationMarker = L.marker(initialPosition).addTo(map);
        locationMarker.bindPopup(`Latitude: ${latitude}, Longitude: ${longitude}`).openPopup();

        // Step 4: Draw trajectory on map
        const trajectoryLine = L.polyline(trajectory, {color: "white", weight: 3, opacity: 1, dashArray: null}) // Draw trajectory
            .setStyle({stroke: true, color: "white", weight: 3, fillColor: "black", fillOpacity: 1}) // Style trajectory line
            .addTo(map);

        // Fit map bounds to trajectory
        map.fitBounds(trajectoryLine.getBounds());

        // Save reference to the drawn path for future use (optional)
        missionPlanSidebar.$data.drawnPath = trajectoryLine;

    } catch (error) {
        console.error("Failed to calculate trajectory:", error);
        alert("An error occurred while calculating the trajectory. Please try again.");
    }
});

let mapMarkers = []; // Array to store map markers

function clearMapMarkers() { // Utility function to remove all markers from the map
    mapMarkers.forEach(marker => map.removeLayer(marker)); // Loop to remove markers
    mapMarkers = []; // Clear marker references after removal
}








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