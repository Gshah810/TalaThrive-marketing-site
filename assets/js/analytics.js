/* ==========================================================================
   Tala Thrive — marketing site analytics
   Plain ES5-ish vanilla JS, no build step, no dependencies.
   Loaded (deferred) in the <head> of every content page, ahead of site.js,
   so window.ttTrack exists before site.js wires its conversion events.

   Two product-analytics tools, both reusing the IDs the live Framer site
   already reports to, so history carries through the migration and nothing new
   is provisioned:
     - Google Analytics 4  (property G-WP0XWRFZHJ, shared with the product app)
     - PostHog             (project 155494, shared with the product app)

   The product app reports to the same GA4 property and PostHog project, so
   every hit from here is tagged surface: "marketing" to stay separable.

   Plus one advertising tool, held to a stricter rule than the two above:
     - Meta Pixel          (consent gated, see the Meta Pixel section below)

   Consent: GA4 and PostHog ship ungated, matching the live site. That is a
   deliberate, recorded parity choice. The Meta Pixel is NOT covered by it and
   does not inherit it. An advertising pixel that reports visits to Meta from a
   mental-health site, including the 38 article URLs under /stories/, is a
   different proposition from first-party product analytics, so it stays off
   until marketing consent is explicitly granted. Nothing on the site grants it
   yet, so the pixel is currently inert by design; wiring a cookie banner to
   window.ttSetMarketingConsent is what turns it on.
   ========================================================================== */

(function () {
  'use strict';

  /* ------------------------------------------------------------------------
     CONFIG — the only place these identifiers live.
     ---------------------------------------------------------------------- */

  var GA4_ID = 'G-WP0XWRFZHJ';
  var POSTHOG_KEY = 'phc_vsC4hAEwTphIxEE9JXb7r2OVjdInSktpWoHlfIsxipT';
  var POSTHOG_HOST = 'https://us.i.posthog.com';
  var SURFACE = 'marketing';

  // Meta Pixel, from Events Manager (Data sources > the number under the pixel
  // name). Guarded by metaPixelConfigured() below, so a blanked or mistyped ID
  // disables the pixel rather than reporting to nothing.
  var META_PIXEL_ID = '1546227733368720';

  // localStorage key holding the visitor's marketing-cookie decision.
  // 'granted' loads the pixel; anything else (including absent) does not.
  var MARKETING_CONSENT_KEY = 'tt_marketing_consent';

  /* ------------------------------------------------------------------------
     Google Analytics 4
     Standard gtag loader. surface is set as a user property so it rides along
     with every hit, and hostname (captured automatically) separates this site
     from the product app inside the shared property as a second signal.
     ---------------------------------------------------------------------- */

  (function loadGa4() {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
    document.head.appendChild(s);

    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;

    gtag('js', new Date());
    gtag('set', 'user_properties', { surface: SURFACE });
    gtag('config', GA4_ID);
  })();

  /* ------------------------------------------------------------------------
     PostHog
     Official loader snippet, then a deliberately slim init. The shared
     project's remote config would otherwise switch on session replay,
     surveys, dead-click and broad autocapture; each flag below overrides that
     for this client so a brochure site stays light. Web Vitals is kept: it is
     cheap and directly serves the speed goal of the rebuild.
     person_profiles: 'identified_only' keeps anonymous marketing visitors from
     creating person profiles until they are actually identified.
     ---------------------------------------------------------------------- */

  !function (t, e) { var o, n, p, r; e.__SV || (window.posthog = e, e._i = [], e.init = function (i, s, a) { function g(t, e) { var o = e.split("."); 2 == o.length && (t = t[o[0]], e = o[1]), t[e] = function () { t.push([e].concat(Array.prototype.slice.call(arguments, 0))) } } (p = t.createElement("script")).type = "text/javascript", p.crossOrigin = "anonymous", p.async = !0, p.src = s.api_host.replace(".i.posthog.com", "-assets.i.posthog.com") + "/static/array.js", (r = t.getElementsByTagName("script")[0]).parentNode.insertBefore(p, r); var u = e; for (void 0 !== a ? u = e[a] = [] : a = "posthog", u.people = u.people || [], u.toString = function (t) { var e = "posthog"; return "posthog" !== a && (e += "." + a), t || (e += " (stub)"), e }, u.people.toString = function () { return u.toString(1) + ".people (stub)" }, o = "init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug getPageViewId captureTraceFeedback captureTraceMetric".split(" "), n = 0; n < o.length; n++)g(u, o[n]); e._i.push([i, s, a]) }, e.__SV = 1) }(document, window.posthog || []);

  window.posthog.init(POSTHOG_KEY, {
    api_host: POSTHOG_HOST,
    person_profiles: 'identified_only',
    disable_session_recording: true,
    disable_surveys: true,
    autocapture: false,
    capture_pageview: true,
    capture_pageleave: true,
    capture_performance: { web_vitals: true },
    loaded: function (ph) { ph.register({ surface: SURFACE }); }
  });

  /* ------------------------------------------------------------------------
     Meta Pixel — consent gated

     Unlike GA4 and PostHog above, nothing here runs on page load unless the
     visitor has already granted marketing consent. Until then no request is
     made to connect.facebook.net at all, which is the point: a blocked-by-
     default pixel leaks nothing, whereas Meta's own 'consent' / 'revoke' call
     still requires loading their script first.

     To turn it on, a consent banner calls:
       window.ttSetMarketingConsent(true)    // grant: persists + loads now
       window.ttSetMarketingConsent(false)   // decline/withdraw: persists
     and can read the current state with window.ttHasMarketingConsent().

     Granting mid-session loads the pixel immediately and fires PageView, so a
     visitor who accepts on their first page is still counted on that page.
     ---------------------------------------------------------------------- */

  var metaPixelLoaded = false;

  // An unreplaced placeholder, an empty string or a typo must never reach
  // fbq('init'), which would otherwise start reporting to nothing.
  function metaPixelConfigured() {
    return /^[0-9]{10,20}$/.test(META_PIXEL_ID);
  }

  function hasMarketingConsent() {
    try {
      return localStorage.getItem(MARKETING_CONSENT_KEY) === 'granted';
    } catch (e) {
      return false;   // storage blocked or private mode: treat as no consent
    }
  }

  function loadMetaPixel() {
    if (metaPixelLoaded || !metaPixelConfigured()) return;
    metaPixelLoaded = true;

    /* Official Meta Pixel base code. Defines the fbq stub and queue, then
       injects fbevents.js; calls made before the script arrives are replayed. */
    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return; n = f.fbq = function () {
        n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments)
      };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0';
      n.queue = []; t = b.createElement(e); t.async = !0; t.src = v;
      s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s)
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

    window.fbq('init', META_PIXEL_ID);
    window.fbq('track', 'PageView');
  }

  window.ttHasMarketingConsent = hasMarketingConsent;

  window.ttSetMarketingConsent = function (granted) {
    try {
      localStorage.setItem(MARKETING_CONSENT_KEY, granted ? 'granted' : 'denied');
    } catch (e) { /* consent must still apply for this page view */ }

    if (granted) {
      loadMetaPixel();
      return;
    }
    // Withdrawn after the pixel had already loaded this session: stop it
    // sending anything further. On the next page load it simply never loads.
    try {
      if (window.fbq) window.fbq('consent', 'revoke');
    } catch (e) { /* analytics must never break the page */ }
  };

  if (hasMarketingConsent()) loadMetaPixel();

  /* ------------------------------------------------------------------------
     Site events that map onto a Meta standard event. Standard events are what
     Meta's ad optimisation and reporting understand; everything else is sent
     with trackCustom under its own name, which stays usable for custom
     conversions without pretending to be a standard event.
     Both lead forms and the Klaviyo newsletter are Lead: each one is a person
     handing over contact details, which is exactly what Meta means by Lead.
     ---------------------------------------------------------------------- */

  var META_STANDARD_EVENTS = {
    lead_submit: 'Lead',
    newsletter_signup: 'Lead'
  };

  /* ------------------------------------------------------------------------
     ttTrack — the one event helper the rest of the site calls.
     Forwards a named event with optional properties to every tool that is
     active and never throws, so a blocked or slow analytics load can never
     break a page. Each call is tagged with surface for GA4 (PostHog gets it
     from the super property registered above). The Meta leg is a no-op unless
     the pixel loaded, i.e. unless marketing consent was granted.
     ---------------------------------------------------------------------- */

  window.ttTrack = function (name, props) {
    props = props || {};
    try {
      if (window.posthog && window.posthog.capture) {
        window.posthog.capture(name, props);
      }
    } catch (e) { /* analytics must never break the page */ }
    try {
      if (window.gtag) {
        var gaProps = {};
        for (var k in props) {
          if (Object.prototype.hasOwnProperty.call(props, k)) gaProps[k] = props[k];
        }
        gaProps.surface = SURFACE;
        window.gtag('event', name, gaProps);
      }
    } catch (e) { /* analytics must never break the page */ }
    try {
      if (window.fbq) {
        var standard = META_STANDARD_EVENTS[name];
        if (standard) window.fbq('track', standard, props);
        else window.fbq('trackCustom', name, props);
      }
    } catch (e) { /* analytics must never break the page */ }
  };
})();
