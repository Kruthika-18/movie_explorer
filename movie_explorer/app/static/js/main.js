/**
 * MovieHub Explorer - Main JavaScript File
 * Adds interactive features to the frontend.
 */

// ── Run after DOM is loaded ──
document.addEventListener('DOMContentLoaded', function () {

  // Auto-dismiss flash alerts after 4 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 4000);
  });

  // ── Search bar: show spinner on submit ──
  const searchForms = document.querySelectorAll('form[action*="search"]');
  searchForms.forEach(form => {
    form.addEventListener('submit', function (e) {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>';
        btn.disabled = true;
      }
    });
  });

  // ── Image lazy loading fallback ──
  // Already handled by onerror in HTML templates

  // ── Confirm delete actions ──
  const deleteForms = document.querySelectorAll('[data-confirm]');
  deleteForms.forEach(form => {
    form.addEventListener('submit', function (e) {
      const msg = this.getAttribute('data-confirm');
      if (!confirm(msg || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  // ── Smooth scroll to reviews section ──
  const reviewLink = document.querySelector('a[href="#reviews"]');
  if (reviewLink) {
    reviewLink.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector('#reviews').scrollIntoView({ behavior: 'smooth' });
    });
  }

});

/**
 * Copy share link to clipboard.
 * Called from the detail page share button.
 */
function copyShareLink() {
  const url = window.location.href;
  navigator.clipboard.writeText(url).then(() => {
    // Show a toast notification
    showToast('Link copied! Share it with friends 🎬', 'success');
  }).catch(() => {
    prompt('Copy this link:', url);
  });
}

/**
 * Display a temporary toast notification.
 * @param {string} message - The message to show
 * @param {string} type - Bootstrap color type ('success', 'danger', etc.)
 */
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container') || createToastContainer();
  
  const toastEl = document.createElement('div');
  toastEl.className = `toast align-items-center text-bg-${type} border-0 show`;
  toastEl.setAttribute('role', 'alert');
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto"
              data-bs-dismiss="toast"></button>
    </div>
  `;
  
  container.appendChild(toastEl);
  
  // Auto-remove after 3 seconds
  setTimeout(() => toastEl.remove(), 3000);
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
  container.style.zIndex = '9999';
  document.body.appendChild(container);
  return container;
}
