new DataTable('#satelliteTable',{
    lengthMenu: [5,10, 15, 20],
    responsive: true,
    scrollX: true,
    autoWidth: false,
    columnDefs: [
        { targets: 0, width: '10%' },   // Name column
        { targets: 1, width: '45%' },   // TLE column
        { targets: 2, width: '8%', className: 'text-center item-center' },   // Center Auto Tracking column
        { targets: 3, width: '8%', className: 'text-center item-center' },   // Center Orbit Status column
        { targets: 4, width: '10%', className: 'text-right item-center' },   // Align Updated column to right
        { targets: 5, width: '10%', className: 'text-right item-center' },   // Align Created column to right
        { targets: 6, width: '3%', className: 'text-center item-center' },   // Align Created column to right
        { targets: [1, 6], orderable: false },  // Disable sorting on TLE column
        { targets: [2,3,4], searchable: false }  // Disable searching on TLE column
    ],
    pageLength: 7,
    language: {
        search: '',
        lengthMenu: 'Rows per page _MENU_',
        searchPlaceholder: "Search",
        info: "_START_ - _END_ of _TOTAL_ items",
        paginate: {
            next: 'Next',
            previous: 'Prev'
        }
    }
});

function fetchSatellites(selectedGroup, updateSatellites, setLoadingState) {
    if (!selectedGroup) {
        alert("Please select a TLE group.");
        return;
    }

    setLoadingState(true);

    fetch(`/fetch_satellites/?group=${selectedGroup}`)
        .then(response => response.json())
        .then(data => {
            updateSatellites(data.satellites);
            setLoadingState(false);
        })
        .catch(error => {
            console.error("Error fetching satellites:", error);
            setLoadingState(false);
        });
}

function addSatellite(formData, onSuccess) {

    fetch('/add_satellite/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            onSuccess();
        } else {
            alert('Error adding satellite.');
        }
    })
    .catch(error => {
        console.error('Error adding satellite:', error);
    });
}

window.fetchSatellites = fetchSatellites;
window.addSatellite = addSatellite;

document.getElementById('edit-satellite-form').addEventListener('submit', function(event) {
  event.preventDefault();

  // Collect form data
  const formData = new FormData(this);

  // Send AJAX request to update the satellite
  fetch('/update_satellite/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
    },
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Close modal and show success message
      // alert('Satellite updated successfully!');
      location.reload();
    } else {
      // Handle error
      alert('Error updating satellite.');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Error updating satellite.');
  });
});

document.getElementById('delete-satellite-form').addEventListener('submit', function(event) {
  event.preventDefault();

  const formData = new FormData(this);
    // console.log([...formData]);

  // Send AJAX request to delete the satellite
  fetch('/delete_satellite/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
    },
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
        location.reload();
      // alert('Satellite deleted successfully!');
    } else {
      alert(`Error deleting satellite: ${data.error}`);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Error deleting satellite');
  });
});

