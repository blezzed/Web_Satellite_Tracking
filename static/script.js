// Select all navigation items
const navItems = document.querySelectorAll('.nav-item');

// Loop through each item and listen for a click event
navItems.forEach(item => {
  console.log("bg cvnvn ")
  item.addEventListener('click', () => {
    // Remove 'active' class from all items
    navItems.forEach(i => i.classList.remove('active'));
    console.log("clicked ")
    // Add 'active' class to the clicked item
    item.classList.add('active');
  });
});

