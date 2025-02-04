import {formatTime} from './script.js';

export function displayMissionPlans(data, missionPlanContainer) {

    missionPlanContainer.innerHTML = data.map(plan => `
        <div x-data="{ 
                openDeleteModal: false, 
                openPlanModal: false,
                missionPlanId: null, 
                async deleteMissionPlan() {
                    if (!this.missionPlanId) {
                        alert('No mission plan ID provided.');
                        return;
                    }
                    try {
                        const response = await fetch('/api/mission_plans/' + this.missionPlanId + '/', {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                            },
                        });
                        if (response.ok) {
                            alert('Mission plan deleted successfully!');
                            document.location.reload();
                        } else {
                            const errorData = await response.json();
                            alert(errorData.error || 'Failed to delete the mission plan.');
                        }
                    } catch (error) {
                        console.error('Error deleting mission plan:', error);
                        alert('An error occurred while processing your request.');
                    }
                }
            }" class="storage-card-tile group" >
            <div class="w-full" @click="openPlanModal = true; $nextTick(() => initializeLeafletMap('map-${plan.id}', ${plan.location.latitude}, ${plan.location.longitude}, ${JSON.stringify(plan.trajectory || [])}));">
                <span class="flex flex-row">
                    <h4 class="mr-3 font-bold">${plan.satellite || "Unknown Satellite"}</h4>
                    <p>(${new Date(plan.rise_time).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                })})</p>
                </span>
                <div class="flex flex-row justify-between">
                    <div class="flex flex-col">
                        <p>Max Elevation: ${plan.max_elevation}°</p>
                        <p>Sun illumination: ${plan.sun_illumination || "N/A"}</p>
                        <p>Location: ${plan.location ? `(${plan.location.latitude}, ${plan.location.longitude})` : "Unknown Location"}</p>
                    </div>
                    <div class="flex flex-col">
                        <p>Rise Time: ${formatTime(plan.rise_time)}</p>
                        <p>Set Time: ${formatTime(plan.set_time)}</p>
                        <div  class="flex flex-row justify-end">
                            <a href="javascript:void(0);" 
                               @click="$event.stopPropagation(); openDeleteModal = !openDeleteModal;  missionPlanId = ${plan.id};"
                               class="hidden group-hover:block border rounded-[8px] px-2 py-1 text-red-500 hover:bg-red-500 hover:text-red-50 transition duration-500">
                                <i class="fa-regular fa-trash-can"></i>
                            </a>
                            
                        </div>
                    </div>
                </div>
            </div>
            
            
            <div x-show="openDeleteModal" 
                 @keydown.escape.window="openDeleteModal = false" 
                 @click.away="openDeleteModal = false" 
                 x-cloak 
                 class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
                <div class="bg-white rounded-lg shadow-lg max-w-lg w-full p-6">
                    <form id="delete-mission-plan--${plan.id}" @submit.prevent="deleteMissionPlan"  action="javascript:void(0);" method="post">
                        <input type="hidden" id="delete-mission-plan--${plan.id}" name="mission_plan_id" value="{{ mission_plan.id }}">
                        <div class="text-center">
                            <span class="text-4xl text-red-600">
                                <i class="ti ti-trash-x"></i>
                            </span>
                            <h4 class="mt-4 text-lg font-semibold">Confirm Deletion</h4>
                            <p class="mt-2 text-gray-600">You want to delete this Mission Plan. This can't be undone once deleted.</p>
                            <div class="mt-6 flex justify-center">
                                <a href="javascript:void(0);" 
                                   @click="openDeleteModal = false" 
                                   class="bg-gray-200 text-gray-800 px-6 py-2 rounded-md mr-4">Cancel</a>
                                <button type="submit" class="bg-red-600 text-white px-6 py-2 rounded-md">Yes, Delete</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- Plan Modal -->
            <div x-show="openPlanModal"
                 @keydown.escape.window="openPlanModal = false"
                 x-cloak
                 class="fixed inset-0 z-[10001] flex items-center justify-center bg-black bg-opacity-50 font-poppins">
                <div class="bg-white rounded-lg max-w-6xl w-full p-6 shadow-lg">
                    <!-- Modal Header -->
                    <div class="modal-header flex items-center justify-between p-4 bg-rifleBlue  text-rifleBlue-100 rounded-t-md">
                        <div>
                            <h4 class="text-lg font-bold">
                                Selected Location:
                            </h4>
                            <!--<p class="text-sm text-rifleBlue-100 text-opacity-50 overflow-hidden whitespace-nowrap text-ellipsis max-w-full">
                                <strong>Latitude:</strong> <span x-text="latitude"></span>
                            </p>
                            <p class="text-sm text-rifleBlue-100 text-opacity-50 overflow-hidden whitespace-nowrap text-ellipsis max-w-full">
                                <strong>Longitude:</strong> <span x-text="longitude"></span>
                            </p>-->
                        </div>
                      <button type="button" class="btn-close text-rifleBlue-100" @click="openPlanModal = false">
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
    
                    <div id="map-${plan.id}" class="flex flex-col h-[55vh] p-2 overflow-y-auto space-y-4">
                        
                    </div>
    
                    <!-- Modal Actions -->
                    <div class=" mt-1 flex justify-end space-x-2">
                        <button type="button"
                                class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300" 
                                @click="openPlanModal = false">
                            close
                        </button>
                        <button type="button" class="calculate-trajectory-button bg-rifleBlue text-rifleBlue-100 py-2 px-3 rounded disabled:bg-gray-100 disabled:text-gray-600"
                            @click=""
                            >Calculate trajectory
                        </button>
                    </div>
                </div>
            </div>

        </div>
    `).join('');
}
