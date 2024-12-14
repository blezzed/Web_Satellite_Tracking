

document.addEventListener("DOMContentLoaded", () => {
    let selectedSatellite = '';
    const satelliteItems = document.querySelectorAll('.sat-item[data-satellite]');
    const passContainer = document.getElementById('pass-container'); // Adjust ID if necessary

    satelliteItems.forEach(item => {
        item.addEventListener('click', () => {
            const satelliteName = item.getAttribute('data-satellite');

            satelliteItems.forEach(i => i.classList.remove('active-sidebar'));

            if(selectedSatellite !== satelliteName){
                item.classList.add('active-sidebar');
                selectedSatellite=satelliteName;
            }else {
                selectedSatellite = '';
            }


            fetch(`/storage?satellite_name=${selectedSatellite}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest' // Important for detecting AJAX requests in Django
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Clear the container
                    passContainer.innerHTML = '';

                    // Add new pass data
                    data.pass_data.forEach(pass => {
                        const formattedDate = formatDate(pass.rise_pass_time);
                        const riseTime = formatTime(pass.rise_pass_time); // Format rise_pass_time
                        const setTime = formatTime(pass.set_pass_time);

                        passContainer.innerHTML += `
                            <div class="storage-card-tile group">
                                <span class="flex flex-row">
                                    <h4 class="mr-3 font-bold">${ pass.satellite_name }</h4>
                                    <p>(${formattedDate})</p>
                                </span>
                                <div class="flex flex-row justify-between">
                                    <div class="flex flex-col">
                                        <p>Max Elevation: ${ pass.max_elevation }°</p>
                                        <p>Azimuth: ${ pass.azimuth }°</p>
                                        <p>Distance: ${ pass.distance } km</p>
                                    </div>
                                    <div class="flex flex-col">
                                        <p>Rise Time: ${riseTime}</p>
                                        <p>Set Time: ${setTime}</p>
                                        
                                        <div x-data="{ openDeleteModal: false,}" class="flex flex-row justify-end">
                                            
                                            <a href="javascript:void(0);" @click="openDeleteModal = !openDeleteModal"
                                                class="hidden group-hover:block border rounded-[8px] px-2 py-1 text-red-500 hover:bg-red-500 hover:text-red-50 transition duration-500">
                                                <i class="fa-regular fa-trash-can"></i>
                                            </a>
                                            
                                            <!-- Delete Modal -->
                                            <div x-show="openDeleteModal" 
                                                @keydown.escape.window="openDeleteModal = false" 
                                                @click.away="openDeleteModal = false" 
                                                x-cloak 
                                                class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
                                                <div class="bg-white rounded-lg shadow-lg max-w-lg w-full p-6">
                                                    <form id="delete-satellite-form" action="javascript:void(0);" method="post">
                                                  
                                                        <!-- Hidden satellite_id field -->
                                                        <input type="hidden" id="delete-satellite-id" name="satellite_id">
                                                        <div class="text-center">
                                                            <span class="text-4xl text-red-600">
                                                                <i class="ti ti-trash-x"></i>
                                                            </span>
                                                            <h4 class="mt-4 text-lg font-semibold">Confirm Deletion</h4>
                                                            <p class="mt-2 text-gray-600">You want to delete this Data. This can't be undone once deleted.</p>
                                                            <div class="mt-6 flex justify-center">
                                                                <a href="javascript:void(0);" @click="openDeleteModal = false" class="bg-gray-200 text-gray-800 px-6 py-2 rounded-md mr-4">Cancel</a>
                                                                <button type="submit" class="bg-red-600 text-white px-6 py-2 rounded-md">Yes, Delete</button>
                                                            </div>
                                                        </div>
                                                    </form>
                                                </div>
                                            </div>
                                            <!-- /Delete Modal -->
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                })
                .catch(error => console.error('Error:', error));
        });
    });

    // Function to format date as "M d Y"
    function formatDate(isoDate) {
        const date = new Date(isoDate);
        const options = { month: 'short', day: 'numeric', year: 'numeric' }; // Matches "M d Y"
        return date.toLocaleDateString('en-US', options);
    }

    // Function to format time as "H:i"
    function formatTime(isoDate) {
        const date = new Date(isoDate);
        const hours = date.getHours().toString().padStart(2, '0'); // Ensure 2 digits
        const minutes = date.getMinutes().toString().padStart(2, '0'); // Ensure 2 digits
        return `${hours}:${minutes}`;
    }
});
