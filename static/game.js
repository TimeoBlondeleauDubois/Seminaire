document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('lettre').focus();
    document.addEventListener('click', function(event) {
        if (event.target !== document.getElementById('lettre')) {
            document.getElementById('lettre').focus();
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('lettre').focus();
    document.getElementById('lettre').addEventListener('mouseover', function(event) {
    });
});

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
    });
});

