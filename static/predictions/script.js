import {socket_sat_passes, socket_position} from "../script.js";

let satellitePassesData = null;
let selectedSatellite = null;

socket_position.onmessage = function (e) {
    console.log(e.data);
    let data = JSON.parse(e.data);

    // Clear the existing satellite list
    let satList = document.getElementById("satellite-position");
    let activeSatellite = selectedSatellite; // Preserve active satellite
    satList.innerHTML = `<div id="sat_list"></div>`; // Create a div for satellite list

    let satListDiv = document.getElementById("sat_list");
    let newlyCreatedTiles = []; // Array to store tiles for adding listeners
    // Loop through the data.position array to populate the list
    data.position.forEach((satellite) => {
        // Add `data-name` to associate satellite name for filtering
        let satInfo = `
        <div 
          class="satellite-position-tile"
          data-satellite="${satellite.name}" 
          data-click="satellite-tile" 
          data-name="${satellite.name}">
            <h3 class="font-bold text-lg text-rifleBlue">${satellite.name}</h3>
            <div class="w-full flex flex-row justify-between">
                <p>Elv: ${satellite.elevation}°</p>
                <p>Azm: ${satellite.azimuth}°</p>
            </div>
        </div>
        <hr>
    `;

        satListDiv.innerHTML += satInfo; // Append to the list
        newlyCreatedTiles.push(satellite.name); // Track newly created tiles

    });

    // Reapply active-sidebar class to the selected satellite tile
    if (activeSatellite) {
        const activeTile = document.querySelector(`[data-name='${activeSatellite}']`);
        if (activeTile) activeTile.classList.add("active-sidebar");
    }

    // Reattach event listeners for the re-rendered satellite tiles
    newlyCreatedTiles.forEach((satelliteName) => {
        const tile = document.querySelector(`[data-name='${satelliteName}']`);
        if (tile) {
            tile.addEventListener("click", () => filterSatellitePasses(satelliteName));
        }
    });
};

function displayForecasts() {
    if (!satellitePassesData || !Array.isArray(satellitePassesData["satellite_passes"])) {
        console.warn("No valid satellite passes data available.");
        return;
    }

    const satellitePasses = satellitePassesData["satellite_passes"];
    console.log("Satellite Passes Data:", satellitePasses);

    const filteredPasses = selectedSatellite
        ? satellitePasses.filter((pass) => pass.satellite.trim().toLowerCase() === selectedSatellite.trim().toLowerCase())
        : satellitePasses;

    console.log(`Selected Satellite: ${selectedSatellite}`);
    console.log("Filtered Passes:", filteredPasses);

    const groupedData = [];
    for (let i = 0; i < filteredPasses.length; i += 3) {
        const group = filteredPasses.slice(i, i + 3);
        groupedData.push(group);
        console.log(`Grouped Data (${i} to ${i + 3}):`, group);
    }

    const pred_list = document.getElementById("predictions-container");
    let tempHTML = ""; // Batch updates
    groupedData.forEach((_pass) => {
        if (!_pass[0] || !_pass[0].event_time) {
            console.warn("Invalid pass detected:", _pass);
            return;
        }

        const dayDate = new Date(_pass[0].event_time);
        const formattedDay = dayDate.toLocaleString("en-US", { weekday: "short", year: "numeric", month: "short", day: "2-digit" });

        console.log(`Day Date for Pass: ${dayDate}, Formatted Day: ${formattedDay}`);

        tempHTML += `
        <div class="table-container w-full bg-rifleBlue-50">
            <h2 class="text-xl font-bold mb-3">${_pass[0].satellite}</h2>
            <table class="responsive-table">
                <thead>
                    <tr>
                        <th>Time (${formattedDay})</th>
                        <th>Event</th>
                        <th>Elevation</th>
                        <th>Azimuth</th>
                        <th>Distance</th>
                    </tr>
                </thead>
                <tbody>
                    ${_pass.map((event) => {
            const eventDate = new Date(event.event_time);
            const formattedDate = eventDate.toLocaleString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });
            console.log(`Event Details:`, {
                event,
                eventDate,
                formattedDate
            });

            return `
                        <tr>
                            <th scope="row">${formattedDate}</th>
                            <td>${event.event}</td>
                            <td>${event.elevation || "-"}°</td>
                            <td>${event.azimuth || "-"}°</td>
                            <td>${event.distance || "-"} km</td>
                        </tr>
                    `;
        }).join("")}
                </tbody>
            </table>
        </div>
        `;
    });
    pred_list.innerHTML = tempHTML; // Single update

    console.log("Updated Predictions Container HTML.");
}

function filterSatellitePasses(satelliteName) {
    selectedSatellite = selectedSatellite === satelliteName ? null : satelliteName;
    console.log(selectedSatellite ? `Filtering passes for: ${selectedSatellite}` : "Cleared selection. Showing all passes.");


    const satelliteTiles = document.querySelectorAll(".satellite-position-tile[data-click='satellite-tile']");
    // Update the visual state of the selected element
    satelliteTiles.forEach((tile) => {
        if (tile.dataset.satellite === satelliteName) {
            if (selectedSatellite) {
                tile.classList.add("active-sidebar");
            } else {
                tile.classList.remove("active-sidebar"); // Clear if deselected
            }
        } else {
            tile.classList.remove("active-sidebar"); // Deselect other tiles
        }
    });
    displayForecasts();
}

window.filterSatellitePasses = filterSatellitePasses;

socket_sat_passes.onmessage = function (e) {
    try {
        satellitePassesData = JSON.parse(e.data);
    } catch (error) {
        console.error("Error parsing WebSocket message:", error);
    }
    displayForecasts();
};

socket_position.onclose = function(e) {
    console.error('WebSocket closed unexpectedly');
};
displayForecasts();

socket_sat_passes.onclose = function(e) {
    console.error('WebSocket closed unexpectedly');
};