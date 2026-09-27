// Bus Number & Route Finder - Frontend Logic
document.addEventListener('DOMContentLoaded', () => {
  const sourceSelect = document.getElementById('source-select');
  const destSelect = document.getElementById('dest-select');
  const swapBtn = document.getElementById('swap-btn');
  const searchForm = document.getElementById('search-form');

  // Swap Source and Destination selections
  if (swapBtn && sourceSelect && destSelect) {
    swapBtn.addEventListener('click', () => {
      const sourceVal = sourceSelect.value;
      const destVal = destSelect.value;

      sourceSelect.value = destVal;
      destSelect.value = sourceVal;

      // Pulse animation
      swapBtn.style.transform = 'rotate(180deg) scale(1.15)';
      setTimeout(() => {
        swapBtn.style.transform = 'none';
      }, 250);
    });
  }

  // Prevent selecting identical source & destination
  if (searchForm && sourceSelect && destSelect) {
    searchForm.addEventListener('submit', (e) => {
      if (sourceSelect.value && destSelect.value && sourceSelect.value === destSelect.value) {
        e.preventDefault();
        alert('Source and Destination cannot be the same stop. Please choose different locations.');
      }
    });
  }

  // Toggle route stepper scroll / full details view
  const toggleButtons = document.querySelectorAll('.btn-toggle-route');
  toggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.bus-card');
      const timeline = card.querySelector('.route-timeline-container');
      if (timeline) {
        timeline.classList.toggle('expanded');
      }
    });
  });
});
