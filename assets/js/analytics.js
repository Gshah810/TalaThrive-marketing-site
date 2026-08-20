/* ==========================================================================
   Tala Thrive — marketing site analytics
   Plain ES5-ish vanilla JS, no build step, no dependencies.
   Loaded (deferred) in the <head> of every content page, ahead of site.js,
   so window.ttTrack exists before site.js wires its conversion events.

   Two tools, both reusing the IDs the live Framer site already reports to, so
   history carries through the migration and nothing new is provisioned:
     - Google Analytics 4  (property G-WP0XWRFZHJ, shared with the product app)
     - PostHog             (project 155494, shared with the product app)

   The product app reports to the same GA4 property and PostHog project, so
   every hit from here is tagged surface: "marketing" to stay separable.

   No consent gate: the live site ships none today and matching it is the
   brief. This is a deliberate, recorded parity choice, not an oversight.
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
     ttTrack — the one event helper the rest of the site calls.
     Forwards a named event with optional properties to both tools and never
     throws, so a blocked or slow analytics load can never break a page. Each
     call is tagged with surface for GA4 (PostHog gets it from the super
     property registered above).
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
  };
})();
