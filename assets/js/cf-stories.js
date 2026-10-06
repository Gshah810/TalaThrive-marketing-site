/* Plain-anchor filtering for the complete materialized publication collection. */
(() => {
  'use strict';
  const source = document.getElementById('cf-publication-data');
  if (!source) return;
  const data = JSON.parse(source.textContent);
  const params = new URLSearchParams(location.search);
  const category = params.get('category') || '';
  const records = data.records.filter(record => !category || record.category === category);
  const pages = Math.max(1, Math.ceil(records.length / 24));
  const requested = Number(params.get('page') || '1');
  const page = Number.isSafeInteger(requested) ? Math.max(1, Math.min(requested, pages)) : 1;
  const bounded = records.slice((page - 1) * 24, page * 24);
  const featured = document.getElementById('cf-featured');
  const grid = document.getElementById('cf-grid');
  const empty = document.querySelector('#cf-list [data-cf-slot="empty-state"]');
  const pagination = document.getElementById('cf-pagination');
  // Cards are escaped by the standard-library materializer; no article prose is in this payload.
  featured.innerHTML = bounded.slice(0, 1).map(record => record.featured_card).join('');
  featured.hidden = bounded.length === 0;
  grid.innerHTML = bounded.slice(1).map(record => record.card).join('');
  empty.hidden = bounded.length !== 0;
  if (category && !bounded.length) {
    empty.querySelector('h2').textContent = 'More stories on this topic are on their way.';
  }
  document.querySelectorAll('.cf-categories a').forEach(link => {
    const selected = new URL(link.href).searchParams.get('category') || '';
    if (selected === category) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  const href = number => {
    const query = new URLSearchParams();
    if (category) query.set('category', category);
    if (number > 1) query.set('page', String(number));
    return '/stories/' + (query.size ? '?' + query.toString() : '') + '#cf-publications';
  };
  pagination.replaceChildren();
  const addLink = (label, number) => {
    const link = document.createElement('a');
    link.href = href(number);
    link.textContent = label;
    pagination.append(link);
  };
  if (page > 1) addLink('← Newer stories', page - 1);
  const summary = document.createElement('p');
  summary.textContent = 'Page ' + page + ' of ' + pages;
  pagination.append(summary);
  if (page < pages) addLink('Older stories →', page + 1);
  pagination.hidden = records.length === 0;
})();
