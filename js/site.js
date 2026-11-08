// The HTML partials are assembled at build time; this file only handles interactions.
window.scrollSlider = function scrollSlider(button, direction) {
  const slider = button.closest('[data-slider-container]')?.querySelector('[data-slider]');
  if (slider) slider.scrollBy({ left: direction * (slider.clientWidth * 0.8), behavior: 'smooth' });
};

window.openViewer = function openViewer(src) {
  const viewer = document.getElementById('imageViewer');
  const viewerImage = document.getElementById('viewerImage');
  if (!viewer || !viewerImage) return;
  viewerImage.src = src;
  viewer.classList.replace('hidden', 'flex');
  document.body.style.overflow = 'hidden';
};

window.closeViewer = function closeViewer() {
  const viewer = document.getElementById('imageViewer');
  if (!viewer) return;
  viewer.classList.replace('flex', 'hidden');
  document.body.style.overflow = '';
};

document.getElementById('imageViewer')?.addEventListener('click', (event) => {
  if (event.target.id === 'imageViewer') window.closeViewer();
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') window.closeViewer();
});

const fireflies = document.getElementById('fireflies');
if (fireflies) {
  setInterval(() => {
    if (fireflies.children.length >= 20) return;
    const el = document.createElement('div');
    const life = 3000 + Math.random() * 4000;
    el.className = 'firefly';
    el.textContent = Math.floor(Math.random() * 10);
    el.style.left = (Math.random() * 100) + 'vw';
    el.style.top = (Math.random() * 100) + 'vh';
    el.style.fontSize = (10 + Math.random() * 18) + 'px';
    el.style.setProperty('--life', life + 'ms');
    fireflies.appendChild(el);
    setTimeout(() => el.remove(), life);
  }, 500);
}
