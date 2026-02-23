document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('sidebarToggle');
  const shell = document.querySelector('.admin-shell');
  const sidebar = document.getElementById('adminSidebar');
  let overlay = null;

  function createOverlay() {
    overlay = document.createElement('div');
    overlay.className = 'admin-overlay';
    overlay.addEventListener('click', closeSidebar);
    document.body.appendChild(overlay);
    // small timeout to allow transition
    requestAnimationFrame(() => overlay.classList.add('visible'));
  }

  function removeOverlay() {
    if (!overlay) return;
    overlay.classList.remove('visible');
    setTimeout(() => {
      if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
      overlay = null;
    }, 200);
  }

  function openSidebar() {
    shell.classList.add('sidebar-open');
    sidebar.classList.add('open');
    sidebar.setAttribute('aria-hidden', 'false');
    if (window.innerWidth < 900) {
      createOverlay();
      document.body.style.overflow = 'hidden';
    }
  }

  function closeSidebar() {
    shell.classList.remove('sidebar-open');
    sidebar.classList.remove('open');
    sidebar.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    removeOverlay();
  }

  toggle.addEventListener('click', function (e) {
    e.stopPropagation();
    if (sidebar.classList.contains('open')) closeSidebar(); else openSidebar();
  });

  // Close on escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) {
      closeSidebar();
    }
  });

  // Ensure aria-hidden correct on load
  sidebar.setAttribute('aria-hidden', 'true');
});
