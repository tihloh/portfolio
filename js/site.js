const partials = [
  'background', 'navigation', 'hero', 'about', 'credentials', 'experience',
  'services', 'projects', 'technical-skills', 'evidence',
  'training', 'future', 'contact', 'footer', 'image-viewer'
];

async function loadPortfolio() {
  const app = document.getElementById('app');
  try {
    const responses = await Promise.all(partials.map((name) => fetch(`partials/${name}.html`)));
    if (responses.some((response) => !response.ok)) throw new Error('A portfolio section could not be loaded.');
    app.innerHTML = (await Promise.all(responses.map((response) => response.text()))).join('\n');
    app.removeAttribute('aria-live');
    initializePortfolio();
  } catch (error) {
    app.innerHTML = '<p class="min-h-screen grid place-items-center px-6 text-center text-zinc-300">Unable to load the portfolio sections. Please open this site through a web server or its published website.</p>';
    console.error(error);
  }
}

function initializePortfolio() {
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
    document.body.style.overflow = 'auto';
  };
  document.getElementById('imageViewer')?.addEventListener('click', (event) => {
    if (event.target.id === 'imageViewer') window.closeViewer();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') window.closeViewer();
  });
  const container = document.getElementById('fireflies');
  if (!container) return;
  setInterval(() => {
    if (container.children.length >= 20) return;
    const el = document.createElement('div');
    const life = 3000 + Math.random() * 4000;
    el.className = 'firefly';
    el.textContent = Math.floor(Math.random() * 10);
    el.style.left = `${Math.random() * 100}vw`;
    el.style.top = `${Math.random() * 100}vh`;
    el.style.fontSize = `${10 + Math.random() * 18}px`;
    el.style.setProperty('--life', `${life}ms`);
    container.appendChild(el);
    setTimeout(() => el.remove(), life);
  }, 500);
}

loadPortfolio();
