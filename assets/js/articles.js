(() => {
  'use strict';
  const list = document.getElementById('cf-article-list');
  const template = document.getElementById('cf-story-records');
  const categories = document.getElementById('cf-categories');
  if (!list || !template || !categories) return;
  const PAGE_SIZE = 24;
  const records = Array.from(template.content.children);
  const empty = document.getElementById('cf-empty-state');
  const pagination = document.getElementById('cf-pagination');
  const previous = pagination.querySelector('[data-previous]');
  const next = pagination.querySelector('[data-next]');
  const label = pagination.querySelector('[data-page-label]');
  const featured = document.querySelector('[data-cf-slot="featured-articles"]');
  let category = '';
  let page = 1;
  function navigate(selected, number) {
    const hash = new URLSearchParams();
    if (selected) hash.set('category', selected);
    hash.set('page', String(number));
    window.location.hash = hash.toString();
  }
  function render() {
    const hash = new URLSearchParams(window.location.hash.slice(1));
    category = hash.get('category') || '';
    const filtered = records.filter(record => !category || record.dataset.cfCategory === category);
    const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    page = Math.min(pages, Math.max(1, Number.parseInt(hash.get('page'), 10) || 1));
    Array.from(list.children).filter(node => node.matches('article[data-cf-origin]')).forEach(node => node.remove());
    const fragment = document.createDocumentFragment();
    filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE).forEach(record => fragment.appendChild(record.cloneNode(true)));
    list.insertBefore(fragment, template);
    empty.hidden = filtered.length !== 0;
    pagination.hidden = filtered.length <= PAGE_SIZE;
    previous.disabled = page === 1;
    next.disabled = page === pages;
    label.textContent = `Page ${page} of ${pages}`;
    categories.querySelectorAll('button[data-category]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.category === category)));
    if (featured) featured.hidden = category !== '';
  }
  categories.addEventListener('click', event => {
    const button = event.target.closest('button[data-category]');
    if (button && categories.contains(button)) navigate(button.dataset.category, 1);
  });
  previous.addEventListener('click', () => navigate(category, page - 1));
  next.addEventListener('click', () => navigate(category, page + 1));
  window.addEventListener('hashchange', render);
  render();
})();
