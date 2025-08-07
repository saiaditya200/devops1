// JavaScript for handling form submissions, interactivity, etc.

document.addEventListener('DOMContentLoaded', function() {
    // Example: Handling form validation or other interactions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Basic example of form validation
            const inputs = form.querySelectorAll('input[required], textarea[required]');
            let valid = true;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.style.borderColor = 'red';
                } else {
                    input.style.borderColor = '#ddd';
                }
            });
            if (!valid) {
                event.preventDefault(); // Prevent form submission if validation fails
                alert('Please fill in all required fields.');
            }
        });
    });
});
document.addEventListener('DOMContentLoaded', function() {
    var toggleButton = document.getElementById('toggleButton');
    var imageContainer = document.getElementById('imageContainer');
    var scannerButton = document.getElementById('scannerButton');
    var scannerInput = document.getElementById('scannerInput');

    toggleButton.addEventListener('click', function() {
        if (imageContainer.classList.contains('hidden')) {
            imageContainer.classList.remove('hidden');
        } else {
            imageContainer.classList.add('hidden');
        }
    });

    scannerButton.addEventListener('click', function() {
        scannerInput.click(); // Simulate a click on the hidden file input
    });

    scannerInput.addEventListener('change', function(event) {
        if (event.target.files.length > 0) {
            var file = event.target.files[0];
            // You can handle the file here, e.g., send it to a server or show a preview
            console.log('File selected:', file);
        }
    });
});
