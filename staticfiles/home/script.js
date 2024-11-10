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
            <div class="satellite-position-tile">
                <h3 class="font-bold text-lg text-rifleBlue">${satellite.name}</h3>
                <div class="w-full flex flex-row justify-between">
                    <p>Elv: ${satellite.elevation}°</p>
                    <p>Azm: ${satellite.azimuth}°</p>
                </div>
            </div>
            <hr>
        `;

        // Append the satellite data to the sat_list div
        satListDiv.innerHTML += satInfo;
    });
};

socket.onclose = function(e) {
    console.error('WebSocket closed unexpectedly');
};