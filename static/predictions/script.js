
let protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
let socket_sat_passes = new WebSocket(protocol + window.location.host + '/ws/satellite_passes/');
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

socket_sat_passes.onmessage = function(e) {
    let data = JSON.parse(e.data);

    const satellitePasses = data["satellite_passes"];
    const groupedData = [];

    // Loop through the array and group every 3 items together
    for (let i = 0; i < satellitePasses.length; i += 3) {
        groupedData.push(satellitePasses.slice(i, i + 3));
    }

    console.log(groupedData);

    let pred_list = document.getElementById('predictions-container');
    pred_list.innerHTML = ''; // Clear previous content

    groupedData.forEach(_pass => {
// Build the HTML for the satellite pass table
    const dayDate = new Date(_pass[0].event_time);
    const formattedDay = dayDate.toLocaleString("en-US", {
      weekday: "short", // "Thu"
      year: "numeric",  // "2024"
      month: "short",   // "Nov"
      day: "2-digit",   // "07"
    });
    let satPassInfo = `
        <div class="table-container w-full bg-white">
            <h2 class="text-xl font-bold mb-3">${_pass[0].satellite}</h2>
            <table class="responsive-table">
              <thead class="">
                <tr>
                  <th>Time (${formattedDay})</th>
                  <th>Event</th>
                  <th>Elevation</th>
                  <th>Azimuth</th>
                  <th>Distance</th>
                </tr>
              </thead>
              <tbody>
                ${_pass.map(event => {
                    const eventDate = new Date(event.event_time);
                    const formattedDate = eventDate.toLocaleString("en-US", {
                      hour: "2-digit",  // "02"
                      minute: "2-digit", // "35"
                      hour12: false
                    });
                    return `
                    <tr>
                      <th scope="row">${formattedDate}</th>
                      <td>${event.event}</td>
                      <td>${event.elevation}°</td>
                      <td>${event.azimuth}°</td>
                      <td>${event.distance}km</td>
                    </tr>
                `}
                ).join('')}
              </tbody>
            </table>
        </div>
        
    `;

    // Append the HTML for each pass to the container
    pred_list.innerHTML += satPassInfo;
})

};

socket.onclose = function(e) {
    console.error('WebSocket closed unexpectedly');
};

socket_sat_passes.onclose = function(e) {
    console.error('WebSocket closed unexpectedly');
};