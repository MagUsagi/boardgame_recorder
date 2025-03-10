// Display errors in the correct fields
function displayErrors(errors) {
    const errorContainer = document.getElementById('add-player-errors');
    errorContainer.innerHTML = ''; // Clear previous errors

    // Check for 'name' errors and filter out empty strings
    if (errors.name) {
        const filteredErrors = errors.name.filter(error => error.trim() !== '');
        if (filteredErrors.length > 0) {
            errorContainer.innerHTML = filteredErrors.join('<br>');
            errorContainer.style.display = 'block';
        } else {
            errorContainer.style.display = 'none';
        }
    } else {
        errorContainer.style.display = 'none';
    }
}

// Submit form with AJAX
document.querySelector('#addPlayerModal form').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = playersUrl;
        } else {
            console.log('Errors:', data.errors); // 確認用
            displayErrors(data.errors); 
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
