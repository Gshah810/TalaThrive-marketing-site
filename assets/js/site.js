/* ==========================================================================
   Tala Thrive — marketing site behaviour
   Plain ES5-ish vanilla JS, no build step, no dependencies.
   Every block is guarded on element presence, so one file serves every page.
   ========================================================================== */

(function () {
  'use strict';

  /* ------------------------------------------------------------------------
     CONFIG — the only place outbound destinations live.
     See LINKS.md for the full map of where each of these is used.
     ---------------------------------------------------------------------- */

  var FORMS = {
    // Set `endpoint` to a Formspree / Tally / Airtable POST URL and the form
    // will submit there natively. Left empty, the form composes a pre-filled
    // email to `mailto` instead, so nothing is ever silently swallowed.
    partner: {
      endpoint: '',
      mailto: 'support@talathrive.com',
      subject: 'Partnership enquiry via talathrive.com'
    },
    demo: {
      endpoint: '',
      mailto: 'support@talathrive.com',
      subject: 'Demo request via talathrive.com'
    }
  };

  var PRACTITIONER_FORM_AU = 'https://airtable.com/appBY6wdmaf9xevtn/pagNIHsVljQGydOeH/form';
  var PRACTITIONER_FORM_INTL = 'https://airtable.com/app1i6T6CwDlQeouR/paghveMaKvWLuR4Lq/form';

  var BANNER_KEY = 'tt_banner_closed';

  var prefersReducedMotion =
    window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  /* ------------------------------------------------------------------------
     1. Promo banner — dismissal persists across pages and reloads
     ---------------------------------------------------------------------- */

  (function promoBanner() {
    var banner = $('[data-promo]');
    if (!banner) return;

    // A blocking snippet in <head> adds .tt-banner-hidden to <html> before
    // first paint, so a previously dismissed banner never flashes.
    if (document.documentElement.classList.contains('tt-banner-hidden')) {
      banner.remove();
      return;
    }

    var close = $('[data-promo-close]', banner);
    if (close) {
      close.addEventListener('click', function () {
        banner.remove();
        try { localStorage.setItem(BANNER_KEY, '1'); } catch (e) {}
      });
    }
  })();

  /* ------------------------------------------------------------------------
     2. Footer copyright year (computed at runtime)
     ---------------------------------------------------------------------- */

  (function footerYear() {
    var el = $('[data-year]');
    if (el) el.textContent = String(new Date().getFullYear());
  })();

  /* ------------------------------------------------------------------------
     3. Mobile menu
     ---------------------------------------------------------------------- */

  (function mobileMenu() {
    var burger = $('[data-burger]');
    var menu = $('[data-mobile-menu]');
    if (!burger || !menu) return;

    var iconOpen = $('[data-icon-open]', burger);
    var iconClose = $('[data-icon-close]', burger);

    burger.addEventListener('click', function () {
      var open = menu.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', String(open));
      // `.hidden` is an HTMLElement property; these are SVG elements, so the
      // attribute has to be toggled directly.
      if (iconOpen) iconOpen.toggleAttribute('hidden', open);
      if (iconClose) iconClose.toggleAttribute('hidden', !open);
    });
  })();

  /* ------------------------------------------------------------------------
     4. Smooth-scroll to in-page anchors, clearing the sticky header
     ---------------------------------------------------------------------- */

  (function anchorScroll() {
    var HEADER_OFFSET = 70;

    $$('a[href^="#"]').forEach(function (link) {
      var id = link.getAttribute('href');
      if (!id || id === '#') return;

      link.addEventListener('click', function (e) {
        var target = document.getElementById(id.slice(1));
        if (!target) return;
        e.preventDefault();
        window.scrollTo({
          top: target.getBoundingClientRect().top + window.scrollY - HEADER_OFFSET,
          behavior: prefersReducedMotion ? 'auto' : 'smooth'
        });
      });
    });
  })();

  /* ------------------------------------------------------------------------
     5. FAQ accordions — one open at a time, per list
     ---------------------------------------------------------------------- */

  (function faqAccordions() {
    $$('[data-faq]').forEach(function (list) {
      var buttons = $$('.faq__q', list);

      buttons.forEach(function (btn) {
        btn.addEventListener('click', function () {
          var wasOpen = btn.getAttribute('aria-expanded') === 'true';
          buttons.forEach(function (other) {
            other.setAttribute('aria-expanded', 'false');
          });
          btn.setAttribute('aria-expanded', String(!wasOpen));
        });
      });
    });
  })();

  /* ------------------------------------------------------------------------
     6. "Simple steps" staggered scroll reveal

     Three independent triggers so the cards can never get stuck hidden:
     an immediate check at load, an IntersectionObserver, a scroll listener,
     and a 1.2s safety timeout.
     ---------------------------------------------------------------------- */

  (function stepsReveal() {
    var row = $('.steps-row');
    if (!row) return;

    var cards = $$('.step-card', row);

    if (prefersReducedMotion) {
      row.classList.add('revealed');
      cards.forEach(function (c) { c.classList.add('revealed'); });
      return;
    }

    var done = false;
    var io = null;
    var timer = null;

    function reveal() {
      if (done) return;
      done = true;
      if (io) io.disconnect();
      if (timer) clearTimeout(timer);
      window.removeEventListener('scroll', onScroll);
      row.classList.add('revealed');
      cards.forEach(function (card, i) {
        setTimeout(function () { card.classList.add('revealed'); }, i * 120);
      });
    }

    function inView() {
      var r = row.getBoundingClientRect();
      var h = window.innerHeight || document.documentElement.clientHeight;
      return r.top < h * 0.85 && r.bottom > 0;
    }

    function onScroll() { if (inView()) reveal(); }

    if (inView()) { reveal(); return; }

    if ('IntersectionObserver' in window) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) { if (entry.isIntersecting) reveal(); });
      }, { threshold: 0.2 });
      io.observe(row);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    timer = setTimeout(reveal, 1200);
  })();


  /* ------------------------------------------------------------------------
     8. Practitioners — "Where are you based?" form router
     ---------------------------------------------------------------------- */

  (function locationPicker() {
    var modal = $('[data-picker]');
    if (!modal) return;

    var lastFocused = null;

    function focusable() {
      return $$('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])', modal)
        .filter(function (el) { return !el.disabled && el.offsetParent !== null; });
    }

    function open() {
      lastFocused = document.activeElement;
      modal.hidden = false;
      document.body.style.overflow = 'hidden';
      var f = focusable();
      if (f[0]) f[0].focus();
    }

    function close() {
      modal.hidden = true;
      document.body.style.overflow = '';
      if (lastFocused) lastFocused.focus();
    }

    $$('[data-picker-open]').forEach(function (btn) {
      btn.addEventListener('click', open);
    });

    $$('[data-picker-close]').forEach(function (btn) {
      btn.addEventListener('click', close);
    });

    modal.addEventListener('click', function (e) {
      if (e.target === modal) close();
    });

    // Escape closes; Tab is trapped within the dialog while it is open.
    document.addEventListener('keydown', function (e) {
      if (modal.hidden) return;
      if (e.key === 'Escape') { close(); return; }
      if (e.key === 'Tab') {
        var f = focusable();
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault(); last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault(); first.focus();
        }
      }
    });

    var au = $('[data-picker-au]', modal);
    var intl = $('[data-picker-intl]', modal);

    if (au) au.addEventListener('click', function () {
      window.open(PRACTITIONER_FORM_AU, '_blank', 'noopener');
      close();
    });

    if (intl) intl.addEventListener('click', function () {
      window.open(PRACTITIONER_FORM_INTL, '_blank', 'noopener');
      close();
    });
  })();

  /* ------------------------------------------------------------------------
     9. About Us — click-to-load YouTube facade
     Keeps YouTube's cookies and ~1MB of player JS off the page until asked.
     ---------------------------------------------------------------------- */

  (function videoFacade() {
    var facade = $('[data-video-facade]');
    if (!facade) return;

    facade.addEventListener('click', function () {
      var frame = facade.parentNode;
      var iframe = document.createElement('iframe');
      iframe.src =
        'https://www.youtube-nocookie.com/embed/og1_VMJYBCY?start=1&autoplay=1&rel=0';
      iframe.title = 'Tala Thrive, our story';
      iframe.allow =
        'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      iframe.allowFullscreen = true;
      frame.replaceChild(iframe, facade);
    });
  })();

  /* ------------------------------------------------------------------------
     10. For Businesses — sticky "Request a 20 min demo" button
     Appears once the hero has scrolled away, hides again over the form.
     ---------------------------------------------------------------------- */

  (function stickyCta() {
    var cta = $('[data-sticky-cta]');
    var hero = $('[data-sticky-after]');
    var demo = $('#demo');
    if (!cta || !hero) return;

    function update() {
      var pastHero = hero.getBoundingClientRect().bottom < 0;
      var overDemo = false;

      if (demo) {
        var r = demo.getBoundingClientRect();
        var h = window.innerHeight || document.documentElement.clientHeight;
        overDemo = r.top < h && r.bottom > 0;
      }

      cta.classList.toggle('is-visible', pastHero && !overDemo);
    }

    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  })();

  /* ------------------------------------------------------------------------
     11. Forms

     GitHub Pages serves static files only, so there is no server to POST to.
     Until an endpoint is configured above, submitting composes a pre-filled
     email in the visitor's own mail client. Nothing is captured invisibly.
     ---------------------------------------------------------------------- */

  (function forms() {
    // What a field says, for a human. A <select> whose options carry an
    // explicit `value` submits a machine token rather than its own text —
    // Company size posts the CRM's headcount band (`201-1000`) — so the email
    // body takes the chosen option's label instead. A person reads this, and
    // the label is what the visitor actually picked. The submitted value is
    // untouched; only the wording of the email changes.
    function fieldText(el) {
      if (el.tagName === 'SELECT') {
        var opt = el.options[el.selectedIndex];
        if (opt) return (opt.textContent || '').trim();
      }
      return el.value;
    }

    $$('form[data-form]').forEach(function (form) {
      var config = FORMS[form.getAttribute('data-form')];
      if (!config) return;

      if (config.endpoint) {
        form.action = config.endpoint;
        form.method = 'POST';
        return; // let the browser submit natively
      }

      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!form.reportValidity()) return;

        var lines = [];
        $$('input, select, textarea', form).forEach(function (el) {
          if (!el.name || !el.value) return;
          var label = form.querySelector('label[for="' + el.id + '"]');
          var name = label ? label.textContent.replace(/\s*\(optional\)\s*/i, '').trim() : el.name;
          lines.push(name + ': ' + fieldText(el));
        });

        var href =
          'mailto:' + config.mailto +
          '?subject=' + encodeURIComponent(config.subject) +
          '&body=' + encodeURIComponent(lines.join('\n'));

        window.location.href = href;

        var success = form.parentNode.querySelector('[data-form-success]');
        if (success) {
          form.hidden = true;
          success.hidden = false;
        }
      });
    });
  })();

  /* ------------------------------------------------------------------------
     9. Conditional "Other" free-text reveal for selects
     Any <input data-other-for="selectId"> shows only when that select == "Other".
     ---------------------------------------------------------------------- */

  (function conditionalOther() {
    $$('[data-other-for]').forEach(function (input) {
      var sel = document.getElementById(input.getAttribute('data-other-for'));
      if (!sel) return;
      function sync() {
        var show = sel.value === 'Other';
        input.hidden = !show;
        if (!show) input.value = '';
      }
      sel.addEventListener('change', sync);
      sync();
    });
  })();
})();
