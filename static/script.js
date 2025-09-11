document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (event) {
            const clientId = document.getElementById("client_id").value.trim();
            const clientSecret = document.getElementById("client_secret").value.trim();

            if (!clientId || !clientSecret) {
                event.preventDefault();
                alert("Please fill in both Client ID and Client Secret!");
            }
        });
    }
});
