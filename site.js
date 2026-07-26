/* ---------------------------------------------------------------------------
   Shared behaviour for every page: privacy-friendly analytics + theme toggle.
   Loaded on index.html and stats.html.
   --------------------------------------------------------------------------- */

/* Visits are counted with GoatCounter — no cookies, no personal data, nothing
   that needs a consent banner. It is dormant until a real code is set here.

   To turn it on:
     1. Sign up at https://www.goatcounter.com and pick a code (your subdomain,
        e.g. "tjdoolittle" -> tjdoolittle.goatcounter.com).
     2. Replace the value below with that code.
     3. In GoatCounter's Settings, tick "Allow using the visitor counter" so the
        public Stats page can read the totals, and — if you want the full
        breakdown page to be public too — "Make statistics public".

   That's the only edit needed; index.html, stats.html and the Stats page all
   read this one value. */
window.GOATCOUNTER_CODE = 'thomasdoolittle';

(function () {
  var code = window.GOATCOUNTER_CODE;

  // Load the tracker only once a real code is in place, so the un-configured
  // site makes no external requests and logs no errors.
  if (code && code !== 'YOUR_CODE_HERE') {
    var s = document.createElement('script');
    s.async = true;
    s.src = '//gc.zgo.at/count.js';
    s.setAttribute('data-goatcounter', 'https://' + code + '.goatcounter.com/count');
    document.head.appendChild(s);
  }

  // Theme toggle. The pre-paint snippet in each page's <head> applies a stored
  // choice before first paint; this just handles the click.
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var root = document.documentElement;
      var systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var current = root.getAttribute('data-theme') || (systemDark ? 'dark' : 'light');
      var next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }
})();
