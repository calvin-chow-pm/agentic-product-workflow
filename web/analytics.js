// Shared portfolio analytics: published, top-level pages only.
(() => {
  'use strict';
  if (window.location.hostname !== 'calvin-chow-pm.github.io' || window.self !== window.top) return;
  const tracker = document.createElement('script');
  tracker.defer = true;
  tracker.src = 'https://cloud.umami.is/script.js';
  tracker.dataset.websiteId = '78ff76ec-0238-4898-8376-5f18c9557863';
  tracker.dataset.domains = 'calvin-chow-pm.github.io';
  tracker.dataset.excludeSearch = 'true';
  tracker.dataset.excludeHash = 'true';
  document.head.appendChild(tracker);
})();
