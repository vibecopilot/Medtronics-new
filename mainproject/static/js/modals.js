// Modal Management Functions and Product Loading

function openModal() {
    openModalById("serviceRequestModal");
}

function openTrainingModal() {
    openModalById("trainingModal");
}

function openDemoModal() {
    openModalById("demoModal");
}

function openLoginModal() {
    openModalById("loginModal");
}

function openRegisteredModal() {
    openModalById("registeredModal");
}

function openModalById(modalId) {
    const modal = document.getElementById(modalId);
    const overlay = document.getElementById("modalOverlay");
    
    if (modal && overlay) {
        modal.classList.add("active");
        overlay.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

function closeModal(modalId) {
    const overlay = document.getElementById("modalOverlay");
    
    if (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove("active");
        }
    } else {
        // Close all modals
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove("active");
        });
    }
    
    if (overlay) {
        overlay.classList.remove("active");
    }
    document.body.style.overflow = "auto";
}

// Product loading functions
async function updateProducts(categoryId) {
    const productSelect = document.getElementById('product');
    
    if (!categoryId) {
        productSelect.innerHTML = '<option value="">Select Product</option>';
        return;
    }
    
    try {
        const response = await fetch(`/api/products-by-category/${categoryId}/`);
        const products = await response.json();
        
        productSelect.innerHTML = '<option value="">Select Product</option>';
        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = product.name;
            productSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching products:', error);
        productSelect.innerHTML = '<option value="">Error loading products</option>';
    }
}

async function updateTrainingProducts(categoryId) {
    const productSelect = document.getElementById('training_product');
    
    if (!categoryId) {
        productSelect.innerHTML = '<option value="">Select Product for Training</option>';
        return;
    }
    
    try {
        const response = await fetch(`/api/products-by-category/${categoryId}/`);
        const products = await response.json();
        
        productSelect.innerHTML = '<option value="">Select Product for Training</option>';
        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = product.name;
            productSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching training products:', error);
        productSelect.innerHTML = '<option value="">Error loading products</option>';
    }
}

async function updateDemoProducts(categoryId) {
    const productSelect = document.getElementById('demo_product');
    
    if (!categoryId) {
        productSelect.innerHTML = '<option value="">Select Product for Demo</option>';
        return;
    }
    
    try {
        const response = await fetch(`/api/products-by-category/${categoryId}/`);
        const products = await response.json();
        
        productSelect.innerHTML = '<option value="">Select Product for Demo</option>';
        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = product.name;
            productSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching demo products:', error);
        productSelect.innerHTML = '<option value="">Error loading products</option>';
    }
}

// Form validation
function validateContactNumber(input) {
    const value = input.value.replace(/\D/g, ''); // Remove non-digits
    input.value = value;
    
    if (value.length !== 10) {
        input.setCustomValidity('Contact number must be exactly 10 digits');
    } else {
        input.setCustomValidity('');
    }
}

function validateName(input) {
    const value = input.value.trim();
    const namePattern = /^[a-zA-Z\s]+$/;
    
    if (!namePattern.test(value)) {
        input.setCustomValidity('Name must contain only letters and spaces');
    } else {
        input.setCustomValidity('');
    }
}

function validateAddress(input) {
    const value = input.value.trim();
    
    if (value.length < 10) {
        input.setCustomValidity('Address must be at least 10 characters long');
    } else {
        input.setCustomValidity('');
    }
}

// Form submission with loading states
function handleFormSubmission(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    // Show loading state
    submitButton.innerHTML = '<span class="spinner"></span>Submitting...';
    submitButton.disabled = true;
    
    // Reset after a delay (form will redirect on success)
    setTimeout(() => {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }, 5000);
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Close modal with Escape key
    document.addEventListener("keydown", function(event) {
        if (event.key === "Escape") {
            closeModal();
        }
    });

    // Close modal when clicking overlay
    const overlay = document.getElementById("modalOverlay");
    if (overlay) {
        overlay.addEventListener("click", function() {
            closeModal();
        });
    }
    
    // Add form validation listeners
    document.querySelectorAll('input[name="contact_number"]').forEach(input => {
        input.addEventListener('input', () => validateContactNumber(input));
    });
    
    document.querySelectorAll('input[name="name"]').forEach(input => {
        input.addEventListener('blur', () => validateName(input));
    });
    
    document.querySelectorAll('textarea[name="address"]').forEach(input => {
        input.addEventListener('blur', () => validateAddress(input));
    });
    
    // Add form submission handlers
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => handleFormSubmission(form));
    });
    
    // Set minimum date for demo requests to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        input.min = today;
    });
});