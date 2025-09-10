document.addEventListener('DOMContentLoaded', function() {
    
    hideFlashMessages();
    addFormValidation();
    addPasswordToggle();
});

function hideFlashMessages() {
    var flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.display = 'none';
        }, 5000); 
    });
}

function addFormValidation() {
    var forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            var requiredFields = form.querySelectorAll('input[required]');
            var isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#d9534f';
                } else {
                    field.style.borderColor = '#ddd';
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
}

function addPasswordToggle() {
    var passwordFields = document.querySelectorAll('input[type="password"]');
    
    passwordFields.forEach(function(field) {
        var toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.innerHTML = 'Show';
        toggleButton.style.marginLeft = '10px';
        toggleButton.className = 'btn btn-secondary';
        
        field.parentNode.appendChild(toggleButton);
        
        toggleButton.addEventListener('click', function() {
            if (field.type === 'password') {
                field.type = 'text';
                toggleButton.innerHTML = 'Hide';
            } else {
                field.type = 'password';
                toggleButton.innerHTML = 'Show';
            }
        });
    });
}
