// static/js/loading.js

const overlay = document.getElementById('loading-overlay');
let loadingTimer = null;

window.showLoading = () => {
  // solo mostrar después de 150ms
  loadingTimer = setTimeout(() => {
    overlay.classList.remove('hidden');
    overlay.classList.add('flex');
  }, 150);
};

window.hideLoading = () => {
  clearTimeout(loadingTimer);
  loadingTimer = null;
  overlay.classList.add('hidden');
  overlay.classList.remove('flex');
};

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('form').forEach(form =>
    form.addEventListener('submit', () => window.showLoading())
  );
});
