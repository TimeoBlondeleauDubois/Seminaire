document.getElementById("deconnexion-btn").addEventListener("click", function(event) {
    event.preventDefault();
    document.getElementById("confirmation-modal").style.display = "block";
});

document.getElementById("confirm-btn").addEventListener("click", function() {
    window.location.href = "/";
});

document.getElementById("cancel-btn").addEventListener("click", function() {
    document.getElementById("confirmation-modal").style.display = "none";
});
