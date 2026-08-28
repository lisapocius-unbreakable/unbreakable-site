// Analytics tracking for mybone.health
// Fires Meta Pixel + GA4 events for the key interactions:
//   - InitiateCheckout / begin_checkout on Amazon book link clicks
//   - Lead / sign_up on Kit form submit success
//   - ViewContent / view_item on blog+book pages
(function() {
  'use strict';

  // Small helpers so the code below reads cleanly whether one or both trackers are present
  function fb(eventName, params) {
    if (typeof fbq === 'function') fbq('track', eventName, params);
  }
  function ga(eventName, params) {
    if (typeof gtag === 'function') gtag('event', eventName, params);
  }

  // 1. Amazon book link click -> InitiateCheckout + begin_checkout
  document.addEventListener('click', function(e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (/amazon\.com\/dp\/|amzn\.to\/|amazon\.com\/stores\/|amazon\.com\/author\//i.test(href)) {
      fb('InitiateCheckout', {
        content_name: 'Osteoporosis Book',
        content_category: 'Book',
        content_ids: ['B0GZ271ZWC'],
        currency: 'USD'
      });
      ga('begin_checkout', {
        item_name: 'Osteoporosis Book',
        item_category: 'Book',
        item_id: 'B0GZ271ZWC',
        currency: 'USD',
        outbound: true,
        link_url: href
      });
    }
  }, true);

  // 2. Kit form submit success -> Lead + sign_up
  // Guard against double-firing (custom event + submit fallback within a couple of seconds)
  var leadFiredAt = 0;
  function fireLead(source) {
    var now = Date.now();
    if (now - leadFiredAt < 3000) return;
    leadFiredAt = now;
    fb('Lead', {
      content_name: 'Calcium Protein Cheat Sheet',
      content_category: 'Freebie'
    });
    ga('sign_up', {
      method: 'kit_form',
      content_name: 'Calcium Protein Cheat Sheet',
      content_category: 'Freebie',
      form_trigger: source || 'unknown'
    });
  }

  // Primary: Kit's official success event
  document.addEventListener('convertkit_form_success', function() {
    fireLead('convertkit_form_success');
  });

  // Fallback: any form posting to a Kit domain
  document.addEventListener('submit', function(e) {
    var form = e.target;
    if (!form || form.tagName !== 'FORM') return;
    var action = (form.getAttribute('action') || '').toLowerCase();
    if (action.indexOf('convertkit') !== -1 || action.indexOf('formkit.com') !== -1 || action.indexOf('kit.com') !== -1) {
      fireLead('form_submit');
    }
  }, true);

  // 3. Content view -> ViewContent + view_item, on pages that opt in
  if (document.documentElement.hasAttribute('data-fb-content')) {
    var contentType = document.documentElement.getAttribute('data-fb-content') || 'article';
    var title = document.title || '';
    fb('ViewContent', {
      content_name: title,
      content_category: contentType
    });
    ga('view_item', {
      item_name: title,
      item_category: contentType
    });
  }
})();
