/* ==========================================================================
   Tala Thrive — marketing site behaviour
   Plain ES5-ish vanilla JS, no build step, no dependencies.
   Every block is guarded on element presence, so one file serves every page.
   ========================================================================== */

(function () {
  'use strict';

  // window.ttTrack is defined in analytics.js, which loads first. But that file
  // is named analytics.js — a name ad blockers and privacy filters commonly
  // match — and it loads GA4 and PostHog, which are widely blocked in their own
  // right, so a real share of visitors never execute it. Install a no-op when
  // that happens, so every call site below stays safe without its own guard and
  // analytics being blocked can never affect what a visitor sees (the form
  // success block above all).
  if (typeof window.ttTrack !== 'function') {
    window.ttTrack = function () {};
  }

  /* ------------------------------------------------------------------------
     CONFIG — the only place outbound destinations live.
     See LINKS.md for the full map of where each of these is used.
     ---------------------------------------------------------------------- */

  // The CRM's public website-form endpoint. It authenticates nobody: this page
  // is static and can hold no secret, so a submission proves it came from a
  // human — a Cloudflare Turnstile token, verified server-side — rather than
  // from a credential. See §11 for the two rules that follow from that.
  var CRM_FORM_ENDPOINT =
    'https://ddqnwbqeggjedquobzol.supabase.co/functions/v1/website-form-public';

  // Cloudflare Turnstile site key. Public by design, so committing it is safe;
  // the matching secret key lives in the CRM (Settings → Integrations) and
  // must never appear here. Emptied, both forms fall back to mailto rather
  // than posting submissions the endpoint would reject.
  var TURNSTILE_SITE_KEY = '0x4AAAAAAEOu0dVR7X_r08Pf';

  var FORMS = {
    // `mode: 'fetch'` posts JSON to `endpoint` from the browser and swaps in
    // the success block without navigating away. `mode: 'mailto'` composes a
    // pre-filled email in the visitor's own mail client instead — the fallback
    // for any form with no endpoint, so nothing is ever silently swallowed.
    //
    // `nameFields` are joined with a space to make the single `name` the CRM
    // contract expects; `answerFields` are the JSON keys inside `answers`, and
    // each one names a field in the form. Keys the endpoint does not know are
    // dropped server-side, so adding one here needs a CRM-side change too.
    partner: {
      mode: 'fetch',
      endpoint: CRM_FORM_ENDPOINT,
      kind: 'partnership',
      label: 'partner',   // stable form id for analytics events
      nameFields: ['name'],
      emailField: 'email',
      companyField: '',   // partnerships carry no company
      answerFields: ['location', 'i_am_a', 'partnership_type', 'link', 'message'],
      mailto: 'support@talathrive.com',
      subject: 'Partnership enquiry via talathrive.com'
    },
    demo: {
      mode: 'fetch',
      endpoint: CRM_FORM_ENDPOINT,
      kind: 'enquiry',
      label: 'business',   // stable form id for analytics events
      nameFields: ['first_name', 'last_name'],
      emailField: 'work_email',
      companyField: 'company',
      answerFields: [
        'first_name', 'last_name', 'company_size', 'team_location', 'goal', 'notes'
      ],
      mailto: 'support@talathrive.com',
      subject: 'Demo request via talathrive.com'
    }
  };

  var PRACTITIONER_FORM_AU = 'https://airtable.com/app1i6T6CwDlQeouR/paghveMaKvWLuR4Lq/form';
  var PRACTITIONER_FORM_INTL = 'https://airtable.com/appBY6wdmaf9xevtn/pagNIHsVljQGydOeH/form';

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
      window.ttTrack('practitioner_form_click', { region: 'au' });
      window.open(PRACTITIONER_FORM_AU, '_blank', 'noopener');
      close();
    });

    if (intl) intl.addEventListener('click', function () {
      window.ttTrack('practitioner_form_click', { region: 'intl' });
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

     GitHub Pages serves static files only, so nothing on this page can hold a
     secret. Submissions therefore POST as JSON to the CRM's public endpoint
     and prove they came from a human with a Cloudflare Turnstile token rather
     than with a credential. Two rules follow from that, and neither is
     negotiable:

       - Content-Type is the entire header list. The endpoint's CORS preflight
         permits no other, so an Authorization or apikey header — which is
         exactly what supabase-js would attach — means the POST never leaves
         the browser. That is why this is a bare fetch.
       - A Turnstile token is mandatory, single-use, and expires after about
         five minutes. Every failed submit resets the widget, or the visitor's
         retry fails forever against a spent token.

     The response says only whether the submission was accepted. Every accepted
     one returns {"ok": true}; whether it becomes a lead, is routed to B2C
     follow-up, or matches a suppression list is decided later, server-side,
     and is deliberately not observable from here. So the success block is the
     visitor's only feedback, and no confirmation email follows it.

     A form with no endpoint — or a deploy with no Turnstile site key set —
     falls back to composing a pre-filled email in the visitor's own mail
     client, so nothing is ever silently swallowed.
     ---------------------------------------------------------------------- */

  (function forms() {

    /* -- Turnstile ---------------------------------------------------------
       Rendered explicitly so we hold each widget's id and can reset it.
       ------------------------------------------------------------------- */

    var widgets = [];  // [{ form, id }] — one widget per form on the page

    function widgetFor(form) {
      for (var i = 0; i < widgets.length; i++) {
        if (widgets[i].form === form) return widgets[i].id;
      }
      return null;
    }

    function mountTurnstile(form) {
      var holder = $('[data-turnstile]', form);
      if (!holder || !window.turnstile || widgetFor(form) !== null) return;
      widgets.push({
        form: form,
        id: window.turnstile.render(holder, {
          sitekey: TURNSTILE_SITE_KEY,
          theme: 'light'
        })
      });
    }

    function turnstileToken(form) {
      var id = widgetFor(form);
      return id === null ? '' : (window.turnstile.getResponse(id) || '');
    }

    function resetTurnstile(form) {
      var id = widgetFor(form);
      if (id !== null) window.turnstile.reset(id);
    }

    /* -- Reading the form --------------------------------------------------- */

    // A <select> with a companion "Other" input resolves to a single value:
    // the typed text when "Other" is chosen and something was typed, the
    // select's own value otherwise. Both are never sent. The companion input
    // points at the select by id (`data-other-for="bd-hq"`), which is what
    // the reveal in §12 keys off too.
    function resolveSelect(form, select) {
      var value = (select.value || '').trim();
      var other = select.id ? $('[data-other-for="' + select.id + '"]', form) : null;
      var otherValue = other ? (other.value || '').trim() : '';
      return value === 'Other' && otherValue ? otherValue : value;
    }

    function fieldValue(form, name) {
      var el = name ? form.elements[name] : null;
      if (!el) return '';
      if (el.tagName === 'SELECT') return resolveSelect(form, el);
      return (el.value || '').trim();
    }

    // utm_* parameters off the current URL, capped at the ten the endpoint
    // accepts. Anything else in the query string is none of the CRM's business.
    function utmParams() {
      var utm = {};
      var kept = 0;
      if (!window.URLSearchParams) return utm;
      new URLSearchParams(window.location.search).forEach(function (value, key) {
        if (kept >= 10 || key.indexOf('utm_') !== 0 || !value) return;
        utm[key] = value.slice(0, 200);
        kept++;
      });
      return utm;
    }

    function buildPayload(form, config, token) {
      var answers = {};
      config.answerFields.forEach(function (name) {
        var value = fieldValue(form, name);
        if (value) answers[name] = value;   // empty is treated as absent
      });

      var payload = {
        kind: config.kind,
        turnstile_token: token,
        // The CRM contract has one `name`; the B2B form collects two fields,
        // so they are joined here. The originals still ride along in answers.
        name: config.nameFields.map(function (field) {
          return fieldValue(form, field);
        }).join(' ').trim(),
        email: fieldValue(form, config.emailField),
        answers: answers
      };

      if (config.companyField) payload.company = fieldValue(form, config.companyField);

      var utm = utmParams();
      if (Object.keys(utm).length) payload.utm = utm;

      return payload;
    }

    /* -- Feedback ----------------------------------------------------------- */

    // The error box is a permanent role="alert" that CSS hides while it is
    // empty, so writing to it both shows and announces the message. Toggling
    // `hidden` instead would leave screen readers nothing to announce.
    function showError(form, message) {
      var box = $('[data-form-error]', form);
      if (box) box.textContent = message;
    }

    function hideError(form) {
      var box = $('[data-form-error]', form);
      if (box) box.textContent = '';
    }

    function showSuccess(form) {
      var wrapper = form.closest ? form.closest('[data-form-wrapper]') : null;
      var success = $('[data-form-success]', wrapper || form.parentNode);
      form.hidden = true;
      if (success) success.hidden = false;
    }

    function messageForStatus(status, config) {
      if (status === 403) {
        return 'We could not verify that submission. Please try the check again.';
      }
      if (status === 413) {
        return 'That is a little too long for us to accept. Please shorten it and try again.';
      }
      if (status === 429) {
        return 'That is a lot of submissions from one connection. Please try again later, ' +
          'or email ' + config.mailto + '.';
      }
      return 'Something went wrong. Please email ' + config.mailto + '.';
    }

    /* -- Submitting --------------------------------------------------------- */

    function submitToCrm(form, config) {
      var button = $('[type="submit"]', form);
      // innerHTML, not textContent: the button carries an inline SVG arrow
      // that textContent would eat and never give back.
      var buttonMarkup = button ? button.innerHTML : '';

      var token = turnstileToken(form);
      if (!token) {
        showError(form, window.turnstile
          ? 'Please complete the verification check above.'
          : 'The verification check could not load. Please email ' + config.mailto + '.');
        return;
      }

      // The endpoint refuses a body over 4 KB. Every free-text field carries a
      // maxlength that keeps a real submission far below it, but check anyway:
      // a visitor who somehow gets there should spend a moment reading this
      // rather than one of the five submissions an hour their IP is allowed.
      var body = JSON.stringify(buildPayload(form, config, token));
      if (new Blob([body]).size > 4096) {
        showError(form, messageForStatus(413, config));
        return;
      }

      hideError(form);
      if (button) {
        button.disabled = true;
        button.textContent = 'Sending…';
      }

      function restoreButton() {
        if (!button) return;
        button.disabled = false;
        button.innerHTML = buttonMarkup;
      }

      fetch(config.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },   // and nothing else
        body: body
      }).then(function (response) {
        if (response.ok) {
          showSuccess(form);
          form.reset();
          // The conversion event: a real lead reached the CRM. This runs after
          // showSuccess above, and ttTrack is always defined, so analytics can
          // never delay or block the success confirmation.
          window.ttTrack('lead_submit', { form: config.label, kind: config.kind });
          return;
        }
        // Spent token: the visitor needs a fresh challenge before retrying.
        resetTurnstile(form);
        showError(form, messageForStatus(response.status, config));
        window.ttTrack('lead_submit_error', {
          form: config.label, kind: config.kind, status: response.status
        });
      }).catch(function () {
        resetTurnstile(form);
        showError(form, 'Something went wrong. Please email ' + config.mailto + '.');
        // status 0: the request never got an HTTP reply (offline or blocked).
        window.ttTrack('lead_submit_error', {
          form: config.label, kind: config.kind, status: 0
        });
      }).then(restoreButton);   // never leave a dead form behind
    }

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

    function submitByMail(form, config) {
      var lines = [];
      $$('input, select, textarea', form).forEach(function (el) {
        if (!el.name || !el.value) return;
        var label = form.querySelector('label[for="' + el.id + '"]');
        var name = label ? label.textContent.replace(/\s*\(optional\)\s*/i, '').trim() : el.name;
        lines.push(name + ': ' + fieldText(el));
      });

      window.location.href =
        'mailto:' + config.mailto +
        '?subject=' + encodeURIComponent(config.subject) +
        '&body=' + encodeURIComponent(lines.join('\n'));

      showSuccess(form);
    }

    /* -- Wiring ------------------------------------------------------------- */

    // Posting without a site key would mean a mandatory token we cannot
    // produce, and a 403 on every submission. Fall back rather than break.
    function modeFor(config) {
      return config.mode === 'fetch' && config.endpoint && TURNSTILE_SITE_KEY
        ? 'fetch'
        : 'mailto';
    }

    var live = [];   // forms actually posting to the CRM, so needing a widget

    $$('form[data-form]').forEach(function (form) {
      var key = form.getAttribute('data-form');
      var config = FORMS[key];
      if (!config) return;

      var mode = modeFor(config);

      if (config.mode === 'fetch' && mode !== 'fetch') {
        if (window.console && console.warn) {
          console.warn('Tala Thrive: no Turnstile site key set, so the "' + key +
            '" form is falling back to mailto.');
        }
        var holder = $('[data-turnstile]', form);
        if (holder) holder.hidden = true;
      } else if (mode === 'fetch') {
        live.push(form);
      }

      form.addEventListener('submit', function (e) {
        e.preventDefault();   // the success block is the confirmation, never a redirect
        if (!form.reportValidity()) return;
        if (mode === 'fetch') submitToCrm(form, config);
        else submitByMail(form, config);
      });
    });

    function mountAll() {
      live.forEach(mountTurnstile);
    }

    // The Turnstile script is async, so it can run either side of this file.
    // Cover both: mount now if it has already loaded, and leave the documented
    // onload callback in place for when it has not.
    window.onloadTurnstileCallback = mountAll;
    if (window.turnstile) mountAll();
  })();

  /* ------------------------------------------------------------------------
     12. Conditional "Other" free-text reveal for selects
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

  /* ------------------------------------------------------------------------
     13. Engagement / CTA analytics
     One delegated click listener, so no button needs per-element markup and
     no page HTML changes. Every event goes through ttTrack, which is always
     defined (a no-op if analytics.js was blocked). Kept deliberately narrow:
     the promo banner, the app
     sign-in / sign-up CTAs (including the "Join the tribe" 10%-off button),
     and the shop. Generic outbound clicks are left to GA4 Enhanced
     Measurement rather than doubled up here.
     ---------------------------------------------------------------------- */

  (function ctaTracking() {
    var APP_LOGIN = 'talathrive.com/login';
    var SHOP_HOST = 'shop.talathrive.com';

    function label(el) {
      return (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80);
    }

    document.addEventListener('click', function (e) {
      if (!e.target || !e.target.closest) return;
      var el = e.target.closest('a, button');
      if (!el) return;

      // Promo banner. Only the "Claim your discount" link counts; the close
      // button shares the container and must not fire a promo_click.
      if (el.closest('[data-promo]')) {
        if (el.tagName === 'A') {
          window.ttTrack('promo_click', { label: label(el), href: el.getAttribute('href') || '' });
        }
        return;
      }

      if (el.tagName !== 'A') return;
      var href = el.getAttribute('href') || '';
      if (!href) return;

      // App sign-in / sign-up, including the "Join the tribe" 10%-off button.
      if (href.indexOf(APP_LOGIN) !== -1) {
        window.ttTrack('cta_click', { destination: 'app', label: label(el), href: href });
        return;
      }
      // Shop.
      if (href.indexOf(SHOP_HOST) !== -1) {
        window.ttTrack('cta_click', { destination: 'shop', label: label(el), href: href });
      }
    }, true);
  })();
})();
