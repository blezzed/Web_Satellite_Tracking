import { showSatellitePath } from './leaflet.js';
import {socket_position} from "../script.js";

export let selectedSatelliteName = null;

let isUTC = false;

function updateClock() {``
    const clockElement = document.getElementById('digital-clock');
    const currentTime = new Date();
    let formattedTime;

    if (isUTC) {
        formattedTime = currentTime.toUTCString().split(" ")[4]; // Extract time in HH:MM:SS format
    } else {
        formattedTime = currentTime.toLocaleTimeString('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    clockElement.textContent = formattedTime;
    updateButtonStyles();
}

function updateButtonStyles() {
    const utcBtn = document.getElementById('utc-btn');
    const localBtn = document.getElementById('local-btn');

    if (isUTC) {
        utcBtn.classList.add('border-b-4', 'border-rifleBlue-700');
        localBtn.classList.remove('border-b-4', 'border-rifleBlue-700');
    } else {
        localBtn.classList.add('border-b-4', 'border-rifleBlue-700');
        utcBtn.classList.remove('border-b-4', 'border-rifleBlue-700');
    }
}

document.getElementById('utc-btn').addEventListener('click', () => {
    isUTC = true;
    updateClock();
});

document.getElementById('local-btn').addEventListener('click', () => {
    isUTC = false;
    updateClock();
});

setInterval(updateClock, 1000);
updateClock();

socket_position.onmessage = function (e) {
    console.log(e.data);
    let data = JSON.parse(e.data);

    // Clear the existing satellite list
    let satList = document.getElementById('satellite-position');
    satList.innerHTML = `<div id="sat_list"></div>`; // Create a div for satellite list

    let satListDiv = document.getElementById('sat_list');

    // Loop through the data.position array
    data.position.forEach((satellite) => {
        // Create a div for each satellite's data
        let satInfo = `
            <div class="satellite-position-tile" data-satellite-name="${satellite.name}">
                <h3 class="font-bold text-lg text-rifleBlue">${satellite.name}</h3>
                <div class="w-full flex flex-row justify-between">
                    <p>Elv: ${satellite.elevation}°</p>
                    <p>Azm: ${satellite.azimuth}°</p>
                </div>
            </div>
            <hr>
        `;
        if (satellite.name === selectedSatelliteName) {
            satInfo = `
                <div class="satellite-position-tile active-sidebar" data-satellite-name="${satellite.name}">
                    <h3 class="font-bold text-lg text-rifleBlue">${satellite.name}</h3>
                    <div class="w-full flex flex-row justify-between">
                        <p>Elv: ${satellite.elevation}°</p>
                        <p>Azm: ${satellite.azimuth}°</p>
                    </div>
                </div>
                <hr>
            `;
        }

        // Append the satellite data to the sat_list div
        satListDiv.innerHTML += satInfo;
    });

    // Add event listeners to each satellite tile
    document.querySelectorAll('.satellite-position-tile').forEach((tile) => {
        tile.addEventListener('click', (event) => {
            if (selectedSatelliteName === tile.dataset.satelliteName) {
                // Deselect all if the selected is clicked again
                selectedSatelliteName = null;
                console.log("Showing all paths");
            } else {
                // Select specific satellite
                selectedSatelliteName = tile.dataset.satelliteName;
                console.log(`Showing path for satellite: ${selectedSatelliteName}`);
            }

            // Call `showSatellitePath` with the selected satellite
            showSatellitePath(selectedSatelliteName); // Pass null for all paths

            // Remove the 'active-sidebar' class from all tiles
            document.querySelectorAll('.satellite-position-tile').forEach((t) => t.classList.remove('active-sidebar'));

            // Add the 'active-sidebar' class to the clicked tile if selected
            if (selectedSatelliteName) {
                tile.classList.add('active-sidebar');
            }
        });
    });
};

socket_position.onclose = function (e) {
    console.error('WebSocket closed unexpectedly');
};