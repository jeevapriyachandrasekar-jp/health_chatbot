// Very small in-page notifier
function notify(title, text) {
  if (window.Notification && Notification.permission === "granted") {
    new Notification(title, { body: text });
  } else if (window.Notification && Notification.permission !== "denied") {
    Notification.requestPermission().then(p => {
      if (p === "granted") new Notification(title, { body: text });
    });
  } else {
    // fallback UI
    alert(title + "\n\n" + text);
  }
}
