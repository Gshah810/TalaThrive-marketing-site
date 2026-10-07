(() => {
  'use strict';
  const list = document.getElementById('cf-article-list');
  const catalog = document.getElementById('cf-story-catalog');
  if (!list || !catalog) return;
  const PAGE_SIZE = 24;
  const cards = Array.from(catalog.content.children);
  const navigation = document.querySelector('[data-cf-slot="category-navigation"]');
  const pagination = document.getElementById('cf-pagination');
  const empty = document.getElementById('cf-empty');
  const featured = document.querySelector('[data-cf-slot="featured-articles"]');
  const status = document.getElementById('cf-page-status');
  let currentPage = 1;
  let currentCategory = '';

  function render() {
    const query = new URLSearchParams(location.hash.slice(1));
    currentCategory = query.get('category') || '';
    const matches = cards.filter(card => !currentCategory || card.dataset.cfCategory === currentCategory);
    const pageCount = Math.max(1, Math.ceil(matches.length / PAGE_SIZE));
    const requested = Number(query.get('page') || 1);
    currentPage = Math.min(pageCount, Math.max(1, Number.isFinite(requested) ? Math.floor(requested) : 1));
    const visibleArticles = matches.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
    list.replaceChildren(...visibleArticles.map(card => card.cloneNode(true)));
    empty.hidden = matches.length !== 0;
    empty.querySelector('h2').textContent = currentCategory ? 'No stories in this category yet' : 'New stories are on their way';
    pagination.hidden = pageCount <= 1;
    status.textContent = `Page ${currentPage} of ${pageCount}`;
    pagination.querySelector('[data-page-step="-1"]').disabled = currentPage <= 1;
    pagination.querySelector('[data-page-step="1"]').disabled = currentPage >= pageCount;
    navigation.querySelectorAll('[data-category]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.category === currentCategory));
    });
    if (featured) featured.hidden = Boolean(currentCategory) || currentPage !== 1;
  }

  function navigate(category, page) {
    const query = new URLSearchParams();
    if (category) query.set('category', category);
    if (page > 1) query.set('page', String(page));
    const hash = query.toString();
    if (location.hash.slice(1) === hash) render();
    else location.hash = hash;
  }

  navigation.addEventListener('click', event => {
    const button = event.target.closest('button[data-category]');
    if (button) navigate(button.dataset.category, 1);
  });
  pagination.addEventListener('click', event => {
    const button = event.target.closest('button[data-page-step]');
    if (!button || button.disabled) return;
    navigate(currentCategory, currentPage + Number(button.dataset.pageStep));
    navigation.scrollIntoView({ block: 'start' });
  });
  addEventListener('hashchange', render);
  render();
})();
