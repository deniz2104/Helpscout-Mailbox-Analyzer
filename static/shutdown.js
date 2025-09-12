window.addEventListener("beforeunload", function () {
    navigator.sendBeacon("/shutdown");
});
