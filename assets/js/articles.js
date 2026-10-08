/* Listing previews only; article bodies live on their native detail routes. */
(() => {
  'use strict';
  const payload = document.getElementById('cf-catalog');
  const results = document.getElementById('cf-results');
  const categories = document.getElementById('cf-categories');
  const support = document.getElementById('cf-catalog-support');
  if (!payload || !results || !categories || !support) return;
  const records = JSON.parse(payload.textContent);
  const empty = support.querySelector('[data-cf-slot="empty-state"]');
  const pagination = support.querySelector('[data-cf-slot="pagination"]');
  const featured = document.getElementById('cf-featured');
  const PAGE_SIZE = 24;
  function destination(category, page) {
    return '#' + new URLSearchParams({category, page: String(page)}).toString();
  }
  function pageLink(label, category, page) {
    const link = document.createElement('a');
    link.className = 'cf-page-link';
    link.href = destination(category, page);
    link.textContent = label;
    return link;
  }
  function render() {
    const state = new URLSearchParams(location.hash.slice(1));
    const requested = state.get('category') || 'all';
    const known = Array.from(categories.querySelectorAll('[data-category]')).some(link => link.dataset.category === requested);
    const category = known ? requested : 'all';
    const matching = records.filter(record => category === 'all' || record.category === category);
    const pageCount = Math.max(1, Math.ceil(matching.length / PAGE_SIZE));
    const page = Math.min(pageCount, Math.max(1, Number.parseInt(state.get('page'), 10) || 1));
    const visibleArticles = matching.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
    results.innerHTML = visibleArticles.map(record => record.html).join('\n');
    empty.hidden = matching.length !== 0;
    if (featured) featured.hidden = category !== 'all' || page !== 1;
    categories.querySelectorAll('[data-category]').forEach(link => {
      if (link.dataset.category === category) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    pagination.replaceChildren();
    if (page > 1) pagination.append(pageLink('Previous stories', category, page - 1));
    const status = document.createElement('p');
    status.setAttribute('aria-live', 'polite');
    status.textContent = `Page ${page} of ${pageCount}`;
    pagination.append(status);
    if (page < pageCount) pagination.append(pageLink('Older stories', category, page + 1));
  }
  window.addEventListener('hashchange', render);
  render();
})();
