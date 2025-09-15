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

    const exportBtn = document.getElementById("exportBtn");
    if (exportBtn) {
        fetch("/check_json_files")
            .then(response => response.json())
            .then(data => {
                if (!data.json_files_exist) {
                    exportBtn.textContent = "Run main file first then come back";
                    exportBtn.disabled = true;
                    exportBtn.style.backgroundColor = "#6c757d";
                    exportBtn.style.cursor = "not-allowed";
                }
            })
            .catch(error => {
                console.error('Error checking JSON files:', error);
                exportBtn.textContent = "Run main file first then come back";
                exportBtn.disabled = true;
                exportBtn.style.backgroundColor = "#6c757d";
                exportBtn.style.cursor = "not-allowed";
            });

        exportBtn.addEventListener("click", function() {
            if (!exportBtn.disabled) {
                exportBtn.textContent = "Exporting...";
                exportBtn.disabled = true;
                
                window.location.href = "/export";
                
                setTimeout(function() {
                    exportBtn.textContent = "Export Data into a CSV";
                    exportBtn.disabled = false;
                }, 1000);
            }
        });
    }
});
