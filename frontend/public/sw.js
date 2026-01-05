// KILLER SERVICE WORKER
// This file exists solely to replace the old stored Service Worker and force it to die.

self.addEventListener('install', (event) => {
    // Take over immediately
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    // Unregister myself and everyone else
    event.waitUntil(
        self.registration.unregister()
            .then(() => {
                return self.clients.matchAll();
            })
            .then((clients) => {
                // Force all open tabs to reload to get the fresh non-PWA version
                clients.forEach((client) => client.navigate(client.url));
            })
    );
});
