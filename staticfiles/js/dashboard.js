/* ================================================================
   EduAdmin Pro — Dashboard JS
   ================================================================ */

'use strict';

document.addEventListener('DOMContentLoaded', () => {

  // ── Init Lucide Icons ─────────────────────────────────────────
  if (window.lucide) lucide.createIcons();

  // ── Sidebar Toggle ────────────────────────────────────────────
  const sidebar     = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');
  const toggleBtn   = document.getElementById('sidebarToggle');
  const isMobile    = () => window.innerWidth < 1024;

  // Create overlay
  const overlay = document.createElement('div');
  overlay.className = 'sidebar-overlay';
  document.body.appendChild(overlay);

  function openSidebar() {
    if (isMobile()) {
      sidebar?.classList.add('mobile-open');
      overlay.classList.add('show');
    }
  }
  function closeSidebar() {
    sidebar?.classList.remove('mobile-open');
    overlay.classList.remove('show');
  }
  function toggleDesktop() {
    sidebar?.classList.toggle('collapsed');
    const col = sidebar?.classList.contains('collapsed');
    localStorage.setItem('sidebar-collapsed', col);
  }

  toggleBtn?.addEventListener('click', () => {
    if (isMobile()) {
      sidebar?.classList.contains('mobile-open') ? closeSidebar() : openSidebar();
    } else {
      toggleDesktop();
    }
  });
  overlay.addEventListener('click', closeSidebar);

  // Restore collapsed state
  if (!isMobile() && localStorage.getItem('sidebar-collapsed') === 'true') {
    sidebar?.classList.add('collapsed');
  }
  window.addEventListener('resize', () => { if (!isMobile()) closeSidebar(); });

  // ── Collapsible Nav Groups ────────────────────────────────────
  document.querySelectorAll('[data-nav-group-toggle]').forEach(btn => {
    const group = btn.closest('.nav-group');
    const key   = 'nav-' + btn.dataset.navGroupToggle;
    if (localStorage.getItem(key) !== 'closed') group?.classList.add('open');

    btn.addEventListener('click', () => {
      group?.classList.toggle('open');
      localStorage.setItem(key, group?.classList.contains('open') ? 'open' : 'closed');
      if (window.lucide) lucide.createIcons();
    });
  });

  // ── Dark Mode ─────────────────────────────────────────────────
  const html      = document.documentElement;
  const themeBtn  = document.getElementById('themeToggle');
  const themeIcon = document.querySelector('[data-theme-icon]');

  function applyTheme(dark) {
    html.setAttribute('data-theme', dark ? 'dark' : 'light');
    localStorage.setItem('theme', dark ? 'dark' : 'light');
    if (themeIcon) {
      themeIcon.setAttribute('data-lucide', dark ? 'sun' : 'moon');
      if (window.lucide) lucide.createIcons();
    }
  }
  const savedTheme = localStorage.getItem('theme') || 'dark';
  applyTheme(savedTheme === 'dark');
  themeBtn?.addEventListener('click', () => applyTheme(html.getAttribute('data-theme') !== 'dark'));

  // ── Auto-dismiss Alerts ───────────────────────────────────────
  document.querySelectorAll('.custom-alert').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s, transform 0.4s';
      el.style.opacity = '0'; el.style.transform = 'translateY(-6px)';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // ── Confirm Modal ─────────────────────────────────────────────
  const modal = document.getElementById('confirmModal');
  document.querySelectorAll('[data-confirm-href]').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const msg  = btn.dataset.confirmMessage || 'Are you sure?';
      const href = btn.dataset.confirmHref;
      if (modal) {
        modal.querySelector('[data-confirm-message]').textContent = msg;
        modal.querySelector('#confirmAction').href = href;
        modal.classList.add('show');
      }
    });
  });
  document.querySelectorAll('[data-modal-close]').forEach(b => b.addEventListener('click', () => modal?.classList.remove('show')));
  modal?.addEventListener('click', e => { if (e.target === modal) modal.classList.remove('show'); });

  // ── Toast Notifications ───────────────────────────────────────
  window.showToast = (message, type = 'success') => {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const icons = { success: 'check-circle', error: 'x-circle', warning: 'alert-triangle' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i data-lucide="${icons[type] || 'info'}"></i><span>${message}</span>`;
    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3500);
  };

  // ── Global Search ─────────────────────────────────────────────
  document.getElementById('globalSearch')?.addEventListener('keydown', e => {
    if (e.key === 'Enter' && e.target.value.trim()) {
      window.location.href = '/search/?q=' + encodeURIComponent(e.target.value.trim());
    }
  });

  // ── Photo Preview ─────────────────────────────────────────────
  document.querySelectorAll('input[type="file"][accept*="image"]').forEach(input => {
    input.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = e => {
        let preview = this.closest('.field-wrap')?.querySelector('.photo-preview');
        if (!preview) {
          preview = document.createElement('img');
          preview.className = 'photo-preview';
          preview.style.cssText = 'width:60px;height:60px;border-radius:50%;object-fit:cover;margin-top:8px;border:2px solid var(--border)';
          this.parentNode.appendChild(preview);
        }
        preview.src = e.target.result;
      };
      reader.readAsDataURL(file);
    });
  });

  // ── Counter Animation ─────────────────────────────────────────
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseFloat(el.dataset.count);
    const isFloat = String(target).includes('.');
    let current = 0;
    const step = target / 45;
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = isFloat ? current.toFixed(1) : Math.floor(current);
      if (current >= target) { el.textContent = isFloat ? target.toFixed(isFloat ? 1 : 0) : target; clearInterval(timer); }
    }, 20);
  });

  // ── Table row click ───────────────────────────────────────────
  document.querySelectorAll('[data-row-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', e => {
      if (!e.target.closest('a, button, .row-actions')) {
        window.location.href = row.dataset.rowHref;
      }
    });
  });

});
