

// Select all navigation items
const sidebarItems = document.querySelectorAll('.sidebar-tile');

sidebarItems.forEach(item => {
  item.addEventListener('click', () => {
    // Remove 'active' class from all items
    sidebarItems.forEach(i => i.classList.remove('active'));

    // Add 'active' class to the clicked item
    item.classList.add('active');

    // Navigate to the URL specified in the data-url attribute
    const url = item.getAttribute('data-url');
    if (url) {
      window.location.href = url;
    }
  });
});





