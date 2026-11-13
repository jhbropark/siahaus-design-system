(function () {
  'use strict';

  var MEASUREMENT_ID = 'G-FFGE099JDE';
  var ADS_ID = 'AW-18499844443';
  var ADS_CONVERSION = 'AW-18499844443/0FlfCPm9hJwdENvytPVE';
  var FORM_ID = 'siahaus-project-brief';
  var FORM_ENDPOINT = 'https://formspree.io/f/xaeqleva';
  var LEAD_RELAY_ENDPOINT = 'https://script.google.com/macros/s/AKfycbyNd7HahWaM1sArcknVzvSKrEyhp0sm7Q2NdUlBPSj86HASOzk8MAQuco0LNqwvK-Xi/exec';
  var ATTRIBUTION_KEY = 'siahaus_attribution_v1';
  var CONSENT_KEY = 'siahaus_privacy_consent_v1';
  var CONSENT_VERSION = '2026-10-29';
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  var analyticsReady = false;

  function readConsent() {
    try {
      var saved = JSON.parse(localStorage.getItem(CONSENT_KEY) || 'null');
      return saved && saved.version === CONSENT_VERSION ? saved.value : '';
    } catch (_) { return ''; }
  }

  function saveConsent(value) {
    try { localStorage.setItem(CONSENT_KEY, JSON.stringify({ value: value, version: CONSENT_VERSION, saved_at: new Date().toISOString() })); } catch (_) {}
  }

  function loadAnalytics() {
    if (analyticsReady) return;
    analyticsReady = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', MEASUREMENT_ID, { send_page_view: true, page_title: document.title, page_location: window.location.href });
    window.gtag('config', ADS_ID);
    var gaScript = document.createElement('script');
    gaScript.async = true;
    gaScript.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEASUREMENT_ID;
    document.head.appendChild(gaScript);
  }

  function showConsentBanner() {
    if (document.getElementById('privacy-consent-banner')) return;
    var banner = document.createElement('aside');
    banner.id = 'privacy-consent-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', '분석 및 광고 태그 동의');
    banner.innerHTML = '<div class="privacy-consent-copy"><strong>사이트 이용 안내</strong><p>사이트 개선과 광고 성과 측정을 위해 Google Analytics 및 Google Ads 태그를 사용할 수 있습니다. <a href="/privacy">개인정보 처리 안내</a></p></div><div class="privacy-consent-actions"><button type="button" data-consent="declined">필수 기능만</button><button type="button" class="is-primary" data-consent="accepted">동의하고 계속</button></div>';
    var style = document.createElement('style');
    style.textContent = '#privacy-consent-banner{position:fixed;z-index:100;left:20px;right:20px;bottom:20px;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:18px 20px;background:#050505;color:#fff;box-shadow:0 12px 32px rgba(0,0,0,.2);font-size:13px}#privacy-consent-banner p{margin:5px 0 0;color:#ccc;line-height:1.6}#privacy-consent-banner a{color:#fff;text-decoration:underline;text-underline-offset:3px}.privacy-consent-actions{display:flex;gap:8px;flex:0 0 auto}.privacy-consent-actions button{border:1px solid #666;background:transparent;color:#fff;padding:10px 13px;font:inherit;cursor:pointer}.privacy-consent-actions button.is-primary{border-color:#fff;background:#fff;color:#050505}@media(max-width:640px){#privacy-consent-banner{left:12px;right:12px;bottom:12px;display:block}.privacy-consent-actions{margin-top:14px}}';
    document.head.appendChild(style);
    banner.querySelectorAll('[data-consent]').forEach(function (button) {
      button.addEventListener('click', function () {
        var value = button.getAttribute('data-consent');
        saveConsent(value);
        banner.remove();
        if (value === 'accepted') loadAnalytics();
      });
    });
    document.body.appendChild(banner);
  }

  function readAttribution() {
    var now = new Date().toISOString();
    var saved = {};
    try { saved = JSON.parse(sessionStorage.getItem(ATTRIBUTION_KEY) || '{}'); } catch (_) {}
    if (!saved.first_seen_at) saved.first_seen_at = now;
    if (!saved.landing_page) saved.landing_page = window.location.href;
    if (!saved.referrer) saved.referrer = document.referrer || '';
    saved.last_seen_at = now;
    var params = new URLSearchParams(window.location.search);
    var serviceTag = serviceTagForPage();
    if (serviceTag) saved.service_tag = serviceTag;
    UTM_KEYS.forEach(function (key) { var value = params.get(key); if (value) saved[key] = value; });
    try { sessionStorage.setItem(ATTRIBUTION_KEY, JSON.stringify(saved)); } catch (_) {}
    return saved;
  }

  function track(name, params) {
    if (!analyticsReady || !window.gtag) return;
    window.gtag('event', name, Object.assign({ site_id: 'siahaus', form_id: FORM_ID }, params || {}));
  }

  function projectSlug(href) {
    var match = String(href || '').match(/\/projects\/([^/?#]+)/);
    return match ? match[1] : '';
  }

  function serviceTagForPage() {
    var params = new URLSearchParams(window.location.search);
    var tagged = params.get('service_tag') || params.get('service');
    if (tagged) return tagged.toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '');
    var match = window.location.pathname.match(/^\/services\/([^/?#]+)/i);
    return match ? match[1].toLowerCase() : 'general_inquiry';
  }

  function newLeadId() {
    return 'sia-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
  }

  function setHidden(form, name, value) {
    var field = form.querySelector('[name="' + name + '"]');
    if (field) field.value = value || '';
  }

  function init() {
    var consent = readConsent();
    if (consent === 'accepted') loadAnalytics();
    else if (!consent) showConsentBanner();

    var attribution = readAttribution();
    document.querySelectorAll('a[href*="/projects/"]').forEach(function (link) {
      link.addEventListener('click', function () { track('project_view', { project_slug: projectSlug(link.getAttribute('href')), cta_location: link.closest('.case-card') ? 'case_studies' : 'portfolio' }); }, { once: true });
    });
    document.querySelectorAll('a[href*="#brief"]').forEach(function (link) {
      link.addEventListener('click', function () { track('brief_click', { cta_location: link.classList.contains('project-contact-cta') ? 'project_detail' : 'navigation' }); }, { once: true });
    });

    var form = document.querySelector('.brief-form');
    if (!form) return;
    var note = form.querySelector('.brief-note');
    var followup = form.querySelector('.brief-followup');
    var submit = form.querySelector('.brief-submit');
    setHidden(form, 'service_tag', attribution.service_tag || serviceTagForPage());
    setHidden(form, 'landing_page', attribution.landing_page);
    setHidden(form, 'page_url', window.location.href);
    setHidden(form, 'referrer', attribution.referrer);
    setHidden(form, 'first_seen_at', attribution.first_seen_at);
    setHidden(form, 'last_seen_at', attribution.last_seen_at);
    UTM_KEYS.forEach(function (key) { setHidden(form, key, attribution[key]); });

    var started = false;
    form.addEventListener('focusin', function () {
      if (started) return;
      started = true;
      track('brief_start', { landing_page: attribution.landing_page });
    });

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      if (!form.reportValidity()) return;
      if (submit) { submit.disabled = true; submit.textContent = '접수 중…'; }
      var data = new FormData(form);
      var leadId = newLeadId();
      var relayAttemptedAt = new Date().toISOString();
      data.set('lead_id', leadId);
      data.set('service_tag', attribution.service_tag || serviceTagForPage());
      data.set('relay_version', 'v2');
      data.set('relay_attempted_at', relayAttemptedAt);
      data.set('relay_client_status', 'pending');
      data.set('relay_status', 'pending');
      data.set('submitted_at', relayAttemptedAt);
      data.set('page_url', window.location.href);
      track('brief_submit', { submission_status: 'attempt', service_tag: data.get('service_tag'), lead_id: leadId });
      try {
        var response = await fetch(FORM_ENDPOINT, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
        if (!response.ok) throw new Error('form_submit_failed');
        var relayPayload = new URLSearchParams();
        data.forEach(function (value, key) { if (typeof value === 'string') relayPayload.append(key, value); });
        var relayStatus = 'failed';
        var relayClientStatus = 'failed';
        try {
          var beaconQueued = navigator.sendBeacon && navigator.sendBeacon(LEAD_RELAY_ENDPOINT, relayPayload);
          if (beaconQueued) {
            relayStatus = 'beacon_queued';
            relayClientStatus = 'beacon_queued';
          } else {
            await fetch(LEAD_RELAY_ENDPOINT, { method: 'POST', body: relayPayload, mode: 'no-cors', keepalive: true });
            relayStatus = 'fetch_fallback_queued';
            relayClientStatus = 'fetch_fallback_queued';
          }
        } catch (_) {
          relayStatus = 'failed';
          relayClientStatus = 'failed';
        }
        data.set('relay_status', relayStatus);
        data.set('relay_client_status', relayClientStatus);
        track('generate_lead', { submission_status: 'success', lead_source: 'website', lead_id: leadId, service_tag: data.get('service_tag'), relay_status: relayStatus, relay_client_status: relayClientStatus, landing_page: attribution.landing_page, utm_source: attribution.utm_source || '(none)', utm_medium: attribution.utm_medium || '(none)', utm_campaign: attribution.utm_campaign || '(none)' });
        if (analyticsReady && window.gtag) window.gtag('event', 'conversion', { send_to: ADS_CONVERSION, value: 1.0, currency: 'KRW' });
        if (note) { note.textContent = '브리프가 접수되었습니다. 확인 후 회신드리겠습니다.'; note.setAttribute('data-state', 'success'); }
        if (followup) followup.hidden = false;
        form.querySelectorAll('input, select, textarea, button').forEach(function (field) { field.disabled = true; });
      } catch (error) {
        track('brief_submit', { submission_status: 'error', service_tag: attribution.service_tag || serviceTagForPage() });
        if (submit) { submit.disabled = false; submit.textContent = '다시 보내기 ↗'; }
        if (note) note.textContent = '접수에 실패했습니다. 잠시 후 다시 시도하거나 sia@sia.haus로 문의해 주세요.';
      }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
