import { showSatellitePath } from './leaflet.js'

export let selectedSatelliteName = null;

let socket = new WebSocket('ws://' + window.location.host + '/ws/satellite/');

socket.onmessage = function(e) {
    console.log(e.data);
    let data = JSON.parse(e.data);

    // Clear the existing satellite list
    let satList = document.getElementById('satellite-position');
    satList.innerHTML = `<div id="sat_list"></div>`;  // Create a div for satellite list

    let satListDiv = document.getElementById('sat_list');

    // Loop through the data.position array
    data.position.forEach(satellite => {
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
        if (satellite.name === selectedSatelliteName){
            satInfo = `
            <div class="satellite-position-tile selected-tile" data-satellite-name="${satellite.name}">
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
    document.querySelectorAll('.satellite-position-tile').forEach(tile => {
        tile.addEventListener('click', (event) => {

            if(selectedSatelliteName=== tile.dataset.satelliteName){
                // selectedSatelliteName = null;
            } else {
                selectedSatelliteName = tile.dataset.satelliteName;
                showSatellitePath(selectedSatelliteName);
            }
            console.log(selectedSatelliteName);

            // Remove the 'selected-tile' class from all tiles
        document.querySelectorAll('.satellite-position-tile').forEach(t => t.classList.remove('selected-tile'));

        // Add the 'selected-tile' class to the clicked tile
        tile.classList.add('selected-tile');
        });
    });
};

socket.onclose = function(e) {
    console.error('WebSocket closed unexpectedly');
};