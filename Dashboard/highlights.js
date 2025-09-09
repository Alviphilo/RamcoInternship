document.addEventListener("DOMContentLoaded", function() {
    const rows = document.querySelectorAll("#serverTable tbody tr");
    rows.forEach(row => {
        row.addEventListener("click", () => {
            rows.forEach(r => r.classList.remove("active"));
            row.classList.add("active");
        });
    });
});
