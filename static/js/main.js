// Main JavaScript file for partners_onerai

document.addEventListener('DOMContentLoaded', function() {
  console.log('Partners OneRAI JavaScript loaded');
  
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Initialize popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
  
  // Flash messages auto-close
  const flashMessages = document.querySelectorAll('.alert-dismissible');
  flashMessages.forEach(function(message) {
    setTimeout(function() {
      const closeButton = message.querySelector('.btn-close');
      if (closeButton) {
        closeButton.click();
      }
    }, 5000);
  });
});
