/* Inert card previews only; article bodies remain on their detail routes. */
(() => {
  'use strict';
  const results = document.getElementById('cf-article-results');
  const bank = document.getElementById('cf-article-bank');
  if (!results || !bank) return;
  const grid = document.getElementById('cf-article-list');
  const categories = document.getElementById('cf-category-navigation');
  const pagination = document.getElementById('cf-pagination');
  const empty = document.getElementById('cf-empty-state');
  const count = document.getElementById('cf-result-count');
  const PAGE_SIZE = 24;
  const records = Array.from(bank.content.children);
  const key = value => value.trim().toLowerCase();
  const href = (category, page) => '#' + new URLSearchParams({category, page:String(page)}).toString();
  function render() {
    const query = new URLSearchParams(location.hash.slice(1));
    const category = query.get('category') || '';
    const matching = records.filter(record => !category || key(record.dataset.cfCategory || '') === key(category));
    const pages = Math.max(1, Math.ceil(matching.length / PAGE_SIZE));
    const requested = Number(query.get('page') || 1);
    const page = Number.isSafeInteger(requested) ? Math.min(pages, Math.max(1, requested)) : 1;
    const visibleArticles = matching.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
    grid.replaceChildren(...visibleArticles.map(record => record.cloneNode(true)));
    empty.hidden = matching.length !== 0;
    count.textContent = matching.length ? `${(page - 1) * PAGE_SIZE + 1}–${Math.min(page * PAGE_SIZE, matching.length)} of ${matching.length} stories` : '0 stories';
    categories.querySelectorAll('a').forEach(link => {
      const selected = key(link.dataset.cfCategory || '') === key(category);
      if (selected) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    pagination.replaceChildren();
    const addLink = (label, target) => {
      const link = document.createElement('a');
      link.className = 'tag';
      link.textContent = label;
      link.href = href(category, target);
      pagination.append(link);
    };
    if (page > 1) addLink('Newer stories', page - 1);
    const position = document.createElement('span');
    position.className = 'story-date';
    position.textContent = `Page ${page} of ${pages}`;
    pagination.append(position);
    if (page < pages) addLink('Older stories', page + 1);
  }
  window.addEventListener('hashchange', render);
  render();
})();
