document.addEventListener('DOMContentLoaded', function () {
    // Select elements
    const hideToolbarButton = document.querySelector('.hide-toolbar');
    const showToolbarButton = document.querySelector('.show-toolbar');
    const adminLinks = document.querySelectorAll('.admin-link');

    // If no user is logged in, there's nothing to do, there are no buttons
    if (!hideToolbarButton || !showToolbarButton) return;

    // Hide toolbar logic
    hideToolbarButton.addEventListener('click', function () {
        console.log('hide collaps button');
        hideToolbarButton.style.display = 'none';
        showToolbarButton.style.display = 'block';
        adminLinks.forEach(link => link.style.display = 'none');
    });

    // Show toolbar logic
    showToolbarButton.addEventListener('click', function () {
        showToolbarButton.style.display = 'none';
        hideToolbarButton.style.display = 'block';
        adminLinks.forEach(link => link.style.display = 'block');
    });
});