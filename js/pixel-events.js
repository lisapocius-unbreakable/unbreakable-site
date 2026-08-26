// Meta Pixel custom event tracking for mybone.health
// Fires: InitiateCheckout on Amazon links, Lead on Kit form submit, ViewContent on blog+book pages
(function() {
  'use strict';
  if (typeof fbq !== 'function') return;

  // 1. InitiateCheckout: any click on an Amazon book link
  document.addEventListener('click', function(e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (/amazon\.com\/dp\/|amzn\.to\/|amazon\.com\/stores\/|amazon\.com\/author\//i.test(href)) {
      fbq('track', 'InitiateCheckout', {
        content_name: 'Osteoporosis Book',
        content_category: 'Book',
        content_ids: ['B0GZ271ZWC'],
        currency: 'USD'
      });
    }
  }, true);

  // 2. Lead: ConvertKit / Kit form submit success
  document.addEventListener('convertkit_form_success', function() {
    fbq('track', 'Lead', {
      content_name: 'Calcium Protein Cheat Sheet',
      content_category: 'Freebie'
    });
  });
  // Fallback: watch for submit events on any Kit form
  document.addEventListener('submit', function(e) {
    var form = e.target;
    if (!form || form.tagName !== 'FORM') return;
    var action = (form.getAttribute('action') || '').toLowerCase();
    if (action.indexOf('convertkit') !== -1 || action.indexOf('formkit.com') !== -1 || action.indexOf('kit.com') !== -1) {
      fbq('track', 'Lead', {
        content_name: 'Calcium Protein Cheat Sheet',
        content_category: 'Freebie'
      });
    }
  }, true);

  // 3. ViewContent: fires on pages that opt in via data-fb-content on <html>
  if (document.documentElement.hasAttribute('data-fb-content')) {
    var contentType = document.documentElement.getAttribute('data-fb-content') || 'article';
    var title = document.title || '';
    fbq('track', 'ViewContent', {
      content_name: title,
      content_category: contentType
    });
  }
})();
