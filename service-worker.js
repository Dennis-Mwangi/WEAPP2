self.addEventListener('push', event => {
    let data = {};
    if (event.data) {
        data = event.data.json();
    }

    const options = {
        body: data.message || "Weather alert!",
        icon: "/icon.png", // optional: path to your icon
        badge: "/badge.png", // optional
        data: { url: "/" } // optional: click action
    };

    event.waitUntil(
        self.registration.showNotification(data.title || "🌩️ Weather Alert", options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url || "/")
    );
});
