/**
 * نظام التفاعل والواجهة - منصة الخدمات الاحترافية
 * Global Interactive Scripts & Handlers
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Theme Toggle (Bootstrap 5.3 native support)
  const themeToggles = document.querySelectorAll('.theme-toggle-btn');
  const htmlElement = document.documentElement;

  // Retrieve saved theme or prefer-color-scheme
  const savedTheme = localStorage.getItem('site_theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  
  applyTheme(savedTheme);

  themeToggles.forEach(btn => {
    btn.addEventListener('click', function () {
      const currentTheme = htmlElement.getAttribute('data-bs-theme') || 'light';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
      localStorage.setItem('site_theme', newTheme);
      showToast(newTheme === 'dark' ? 'تم تفعيل الوضع الليلي 🌙' : 'تم تفعيل الوضع النهاري ☀️', 'info');
    });
  });

  function applyTheme(theme) {
    htmlElement.setAttribute('data-bs-theme', theme);
    document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
      const icon = btn.querySelector('i');
      if (icon) {
        if (theme === 'dark') {
          icon.className = 'bi bi-sun-fill text-warning';
        } else {
          icon.className = 'bi bi-moon-stars-fill text-light';
        }
      }
    });
  }

  // 2. Navbar on Scroll
  const navbar = document.querySelector('.main-navbar');
  const backToTopBtn = document.getElementById('backToTopBtn');

  window.addEventListener('scroll', function () {
    if (window.scrollY > 40) {
      if (navbar) navbar.classList.add('scrolled');
      if (backToTopBtn) backToTopBtn.classList.add('visible');
    } else {
      if (navbar) navbar.classList.remove('scrolled');
      if (backToTopBtn) backToTopBtn.classList.remove('visible');
    }
  });

  if (backToTopBtn) {
    backToTopBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // 3. Page Loader dismissal
  const pageLoader = document.getElementById('pageLoader');
  if (pageLoader) {
    setTimeout(function () {
      pageLoader.style.opacity = '0';
      setTimeout(function () {
        pageLoader.style.display = 'none';
      }, 400);
    }, 250);
  }

  // 4. Global Favorite Toggle via AJAX
  document.querySelectorAll('.btn-favorite-trigger').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const serviceId = this.dataset.serviceId;
      if (!serviceId) return;

      const heartIcon = this.querySelector('i');
      const isCurrentlyActive = this.classList.contains('active');

      const textSpan = this.querySelector('span');

      // Optimistic UI update
      if (isCurrentlyActive) {
        this.classList.remove('active');
        if (heartIcon) heartIcon.className = 'bi bi-heart';
        if (textSpan) textSpan.textContent = 'حفظ';
      } else {
        this.classList.add('active');
        if (heartIcon) heartIcon.className = 'bi bi-heart-fill text-danger';
        if (textSpan) textSpan.textContent = 'محفوظ';
      }

      fetch(`/favorites/toggle/${serviceId}/`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken') || ''
        }
      })
      .then(response => {
        if (response.status === 401 || response.status === 403) {
          window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
          return;
        }
        return response.json();
      })
      .then(data => {
        if (data && data.success) {
          showToast(data.message, data.is_favorite ? 'success' : 'info');
        }
      })
      .catch(err => {
        console.log('Favorite toggle notice:', err);
      });
    });
  });

  // Helper: Get CSRF Cookie
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

  // 5. Global Toast Notification helper
  window.showToast = function (message, type = 'success') {
    let container = document.getElementById('toastFloatingContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastFloatingContainer';
      container.className = 'toast-floating-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-custom';
    
    let iconClass = 'bi-check-circle-fill text-success';
    if (type === 'danger' || type === 'error') iconClass = 'bi-exclamation-triangle-fill text-danger';
    if (type === 'info') iconClass = 'bi-info-circle-fill text-info';
    if (type === 'warning') iconClass = 'bi-exclamation-circle-fill text-warning';

    toast.innerHTML = `
      <i class="bi ${iconClass} fs-5"></i>
      <span class="flex-grow-1">${message}</span>
      <button type="button" class="btn-close ms-2" style="font-size: 0.75rem;" aria-label="Close"></button>
    `;

    toast.querySelector('.btn-close').addEventListener('click', function () {
      toast.remove();
    });

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(15px)';
      setTimeout(() => toast.remove(), 400);
    }, 4000);
  };
});
