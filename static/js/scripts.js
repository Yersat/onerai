// Main JavaScript file for onerai

document.addEventListener('DOMContentLoaded', function() {
  console.log('OneRAI JavaScript loaded');
  
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

  // CSRF token handling for AJAX requests
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Set up CSRF token for all AJAX requests
  const csrftoken = getCookie('csrftoken');
  
  // Add CSRF token to all AJAX requests
  document.addEventListener('submit', function(e) {
    // Only handle forms that don't have the CSRF token
    const form = e.target;
    if (form.method && form.method.toLowerCase() === 'post' && !form.querySelector('input[name="csrfmiddlewaretoken"]')) {
      e.preventDefault();
      
      // Add CSRF token to the form
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = csrftoken;
      form.appendChild(csrfInput);
      
      // Submit the form
      form.submit();
    }
  });
});
