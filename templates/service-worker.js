const CACHE_NAME = "geocareergo-v2";

const STATIC_ASSETS = [
    "/",
    "/static/pwa/icon-192.png",
    "/static/pwa/icon-512.png",
    "/static/pwa/favicon-64.png"
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(STATIC_ASSETS))
    );

    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(name => name !== CACHE_NAME)
                    .map(name => caches.delete(name))
            );
        })
    );

    self.clients.claim();
});

self.addEventListener("fetch", event => {
    const request = event.request;

    if (request.method !== "GET") {
        return;
    }

    const url = new URL(request.url);

    if (url.origin !== self.location.origin) {
        return;
    }

    // Never cache private/admin areas
    if (
        url.pathname.startsWith("/admin/") ||
        url.pathname.startsWith("/accounts/") ||
        url.pathname.startsWith("/tests/")
    ) {
        return;
    }

    // Pages: network first, cache fallback
    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request)
                .then(response => {
                    const copy = response.clone();

                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(request, copy);
                    });

                    return response;
                })
                .catch(() => {
                    return caches.match(request)
                        .then(cached => cached || caches.match("/"));
                })
        );

        return;
    }

    // Static files: cache first
    if (url.pathname.startsWith("/static/")) {
        event.respondWith(
            caches.match(request)
                .then(cached => {
                    if (cached) {
                        return cached;
                    }

                    return fetch(request).then(response => {
                        const copy = response.clone();

                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(request, copy);
                        });

                        return response;
                    });
                })
        );
    }
});