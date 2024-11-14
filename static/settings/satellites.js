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
    pageLength: 6,
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

