// LineBred service worker.
// Strategy: cache the app shell on install; serve the shell cache-first so the app
// opens with no signal, and keep data.json network-first so a freshly pushed
// database is picked up as soon as the phone is online again.
const VERSION = "20261112-9fdbd181";
const SHELL = "linebred-shell-" + VERSION;
const DATA  = "linebred-data-" + VERSION;
const SHELL_FILES = [
  "./", "./index.html", "./app.js", "./tokens.css", "./manifest.webmanifest",
  "./logo.png", "./logo-reversed.png",
  "./icon-180.png", "./icon-512.png", "./favicon-32.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(SHELL)
      .then((c) => Promise.allSettled(SHELL_FILES.map((f) => c.add(new Request(f, { cache: "reload" })))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== SHELL && k !== DATA).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // data.json: network first, fall back to the last copy we stored.
  if (url.pathname.endsWith("/data.json") || url.pathname.endsWith("data.json")) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(DATA).then((c) => c.put("data.json", copy));
          }
          return res;
        })
        .catch(() => caches.open(DATA).then((c) => c.match("data.json")))
    );
    return;
  }

  // Everything else: cache first, then network.
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res && res.ok && url.origin === location.origin) {
        const copy = res.clone();
        caches.open(SHELL).then((c) => c.put(req, copy));
      }
      return res;
    }).catch(() => hit))
  );
});
