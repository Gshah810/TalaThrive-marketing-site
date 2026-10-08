/* cf-slot: article-registry — consume the complete metadata collection, not bodies. */
(() => {
  'use strict';
  const source = document.getElementById('cf-records');
  const results = document.getElementById('cf-results');
  const categories = document.getElementById('cf-categories');
  const pagination = document.getElementById('cf-pagination');
  const empty = document.getElementById('cf-empty');
  const archive = document.getElementById('cf-legacy-stories');
  if (!source || !results || !categories || !pagination || !empty || !archive) return;
  const records = JSON.parse(source.textContent);
  const legacy = Array.from(archive.content.querySelectorAll('a.story-card'));
  const PAGE_SIZE = 24;
  const labels = new Map();
  records.forEach(record => labels.set(record.category_key, record.category));
  function pageURL(category, page = 1) {
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    params.set('page', String(page));
    return '?' + params.toString() + '#cf-results';
  }
  function anchor(label, href, className) {
    const link = document.createElement('a');
    link.textContent = label;
    link.href = href;
    link.className = className;
    return link;
  }
  categories.replaceChildren();
  const all = anchor('All stories', pageURL(''), 'tag');
  all.dataset.category = '';
  categories.append(all);
  labels.forEach((label, key) => {
    const link = anchor(label, pageURL(key), 'tag');
    link.dataset.category = key;
    categories.append(link);
  });
  function render() {
    const query = new URLSearchParams(location.search);
    const oldHash = new URLSearchParams(location.hash.slice(1));
    const category = query.get('category') ?? oldHash.get('category') ?? '';
    const requested = Number(query.get('page') ?? oldHash.get('page') ?? 1);
    // Filter ALL publication and legacy metadata before the 24-record page limit.
    const matches = records.filter(record => !category || record.category_key === category || record.category === category);
    const pageCount = Math.max(1, Math.ceil(matches.length / PAGE_SIZE));
    const page = Math.min(pageCount, Math.max(1, Number.isSafeInteger(requested) ? requested : 1));
    const visibleArticles = matches.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
    const fragment = document.createDocumentFragment();
    visibleArticles.forEach(record => {
      if (Number.isInteger(record.legacy_index)) {
        const link = legacy[record.legacy_index].cloneNode(true);
        link.dataset.cfSlot = 'article-link';
        const card = document.createElement('article');
        card.dataset.cfSlot = 'article-card';
        card.append(link);
        fragment.append(card);
      } else {
        const template = document.createElement('template');
        // Only escaped preview metadata, never trusted article_html, is loaded here.
        template.innerHTML = record.card_html;
        fragment.append(template.content.cloneNode(true));
      }
    });
    results.replaceChildren(fragment);
    empty.hidden = matches.length !== 0;
    categories.querySelectorAll('a').forEach(link => {
      const selected = link.dataset.category === category || labels.get(link.dataset.category) === category;
      if (selected) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    pagination.replaceChildren();
    pagination.hidden = pageCount === 1;
    if (page > 1) {
      const previous = anchor('← Previous page', pageURL(category, page - 1), 'back-link');
      previous.rel = 'prev';
      previous.dataset.page = String(page - 1);
      pagination.append(previous);
    }
    const position = document.createElement('span');
    position.className = 'story-date';
    position.setAttribute('aria-live', 'polite');
    position.textContent = `Page ${page} of ${pageCount}`;
    pagination.append(position);
    for (let number = 1; number <= pageCount; number++) {
      const link = anchor(String(number), pageURL(category, number), 'back-link');
      link.setAttribute('aria-label', `Page ${number}`);
      link.dataset.page = String(number);
      if (number === page) link.setAttribute('aria-current', 'page');
      pagination.append(link);
    }
    if (page < pageCount) {
      const next = anchor('Next page — older stories →', pageURL(category, page + 1), 'back-link');
      next.rel = 'next';
      next.dataset.page = String(page + 1);
      pagination.append(next);
    }
  }
  function navigate(event) {
    const link = event.target.closest('a');
    if (!link || !event.currentTarget.contains(link) || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const destination = new URL(link.href, location.href);
    if (destination.origin !== location.origin || destination.pathname !== location.pathname) return;
    event.preventDefault();
    history.pushState(null, '', destination.href);
    render();
    results.focus({preventScroll: true});
    results.scrollIntoView({block: 'start'});
  }
  // Native query links also work on reload, direct entry and modified clicks.
  categories.addEventListener('click', navigate);
  pagination.addEventListener('click', navigate);
  window.addEventListener('popstate', render);
  window.addEventListener('hashchange', render);
  render();
})();
