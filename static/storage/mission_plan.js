import {formatTime} from './script.js';

export function displayMissionPlans(data, missionPlanContainer) {

    missionPlanContainer.innerHTML = data.map(plan => `
        <div class="storage-card-tile group">
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
                    <p>Location: ${plan.location ? `(${plan.location.longitude}, ${plan.location.latitude})` : "Unknown Location"}</p>
                </div>
                <div class="flex flex-col">
                    <p>Rise Time: ${formatTime(plan.rise_time)}</p>
                    <p>Set Time: ${formatTime(plan.set_time)}</p>
                    <div x-data="{ 
                            openDeleteModal: false, 
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
                        }" class="flex flex-row justify-end">
                        <a href="javascript:void(0);" 
                           @click="openDeleteModal = !openDeleteModal; missionPlanId = ${plan.id};"
                           class="hidden group-hover:block border rounded-[8px] px-2 py-1 text-red-500 hover:bg-red-500 hover:text-red-50 transition duration-500">
                            <i class="fa-regular fa-trash-can"></i>
                        </a>
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
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}
