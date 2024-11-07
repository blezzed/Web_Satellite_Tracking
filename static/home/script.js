let socket = new WebSocket('ws://' + window.location.host + '/ws/satellite/');
        let socket_sat_passes = new WebSocket('ws://' + window.location.host + '/ws/satellite_passes/');

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
                    <div class="satellite">
                        <h3>Satellite: ${satellite.name}</h3>
                        <p>Elevation: ${satellite.elevation}°</p>
                        <p>Azimuth: ${satellite.azimuth}°</p>
                        <p>Distance: ${satellite.distance_km} km</p>
                        <p>Latitude: ${satellite.latitude}</p>
                        <p>Longitude: ${satellite.longitude}</p>
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