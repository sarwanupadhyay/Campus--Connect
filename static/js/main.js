
document.addEventListener('DOMContentLoaded', function() {
  // Flash message close functionality
  const closeButtons = document.querySelectorAll('.flash-message .close-btn');
  closeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const message = this.parentNode;
      message.style.opacity = '0';
      setTimeout(() => {
        message.style.display = 'none';
      }, 300);
    });
  });

  // Auto-hide flash messages after 5 seconds
  const flashMessages = document.querySelectorAll('.flash-message');
  flashMessages.forEach(message => {
    setTimeout(() => {
      message.style.opacity = '0';
      setTimeout(() => {
        message.style.display = 'none';
      }, 300);
    }, 5000);
  });

  // Mobile sidebar toggle functionality
  const toggleMobileMenu = () => {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    
    if (!sidebar) return;

    // Create toggle button if it doesn't exist
    if (!document.querySelector('.sidebar-toggle')) {
      const toggleBtn = document.createElement('button');
      toggleBtn.className = 'btn-icon btn-ghost sidebar-toggle';
      toggleBtn.style.position = 'fixed';
      toggleBtn.style.bottom = '1rem';
      toggleBtn.style.right = '1rem';
      toggleBtn.style.zIndex = '30';
      toggleBtn.style.backgroundColor = 'var(--primary-orange)';
      toggleBtn.style.color = 'white';
      toggleBtn.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
      toggleBtn.style.borderRadius = '9999px';
      toggleBtn.style.width = '3rem';
      toggleBtn.style.height = '3rem';
      toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
      
      document.body.appendChild(toggleBtn);
      
      toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('open');
        
        if (sidebar.classList.contains('open')) {
          document.body.appendChild(overlay);
          setTimeout(() => {
            overlay.classList.add('show');
          }, 10);
          this.innerHTML = '<i class="fas fa-times"></i>';
        } else {
          overlay.classList.remove('show');
          setTimeout(() => {
            if (overlay.parentNode) {
              overlay.parentNode.removeChild(overlay);
            }
          }, 300);
          this.innerHTML = '<i class="fas fa-bars"></i>';
        }
      });
      
      // Close sidebar when clicking the overlay
      document.body.addEventListener('click', function(e) {
        if (e.target.classList.contains('sidebar-overlay')) {
          sidebar.classList.remove('open');
          overlay.classList.remove('show');
          setTimeout(() => {
            if (overlay.parentNode) {
              overlay.parentNode.removeChild(overlay);
            }
          }, 300);
          document.querySelector('.sidebar-toggle').innerHTML = '<i class="fas fa-bars"></i>';
        }
      });
    }
  };
  
  // Initialize mobile menu
  if (window.innerWidth < 1024) {
    toggleMobileMenu();
  }
  
  // Recheck on resize
  window.addEventListener('resize', function() {
    if (window.innerWidth < 1024) {
      toggleMobileMenu();
    }
  });
});
