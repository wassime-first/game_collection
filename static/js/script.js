const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');

const tooltipList = [...tooltipTriggerList].map(
    tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl)
);

document.addEventListener("DOMContentLoaded", function () {
    const toastEl = document.querySelector(".toast");

    if (toastEl) {
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    }
});