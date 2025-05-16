// Main JavaScript file for onerai - Consolidated from multiple files
// Includes functionality from vendor.js, charts.js, site-blocker.js, and scripts.js

document.addEventListener('DOMContentLoaded', function() {
  console.log('OneRAI JavaScript loaded');
  
  // ===== Initialize Bootstrap Components =====
  
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
  
  // ===== Flash Messages Auto-Close =====
  
  const flashMessages = document.querySelectorAll('.alert-dismissible');
  flashMessages.forEach(function(message) {
    setTimeout(function() {
      const closeButton = message.querySelector('.btn-close');
      if (closeButton) {
        closeButton.click();
      }
    }, 5000);
  });

  // ===== CSRF Token Handling for AJAX Requests =====
  
  // Function to get CSRF token from cookies
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

  // Get CSRF token
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

  // ===== Chart Functionality =====
  
  // Initialize any charts if needed
  const chartElements = document.querySelectorAll('.chart-container');
  if (chartElements.length > 0) {
    console.log('Charts module loaded');
    // Chart initialization code would go here
  }

  // ===== Site Blocking Functionality =====
  
  // Initialize site blocking features if needed
  console.log('Site blocker module loaded');
  // Site blocking code would go here
});

// ===== Utility Functions =====

// Function to format currency
function formatCurrency(amount, currency = '₸') {
  return `${amount} ${currency}`;
}

// Function to validate email
function isValidEmail(email) {
  const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(String(email).toLowerCase());
}

// Function to apply design filter based on t-shirt color
function applyDesignFilter(designElement, color) {
  if (color === 'black' || color === 'blue' || color === 'green') {
    // For dark t-shirts, add a subtle brightness to the design
    designElement.style.filter = 'brightness(1.2) drop-shadow(0 0 3px rgba(255, 255, 255, 0.3))';
  } else {
    // For light t-shirts, keep normal brightness
    designElement.style.filter = 'drop-shadow(0 0 2px rgba(0, 0, 0, 0.2))';
  }
}
