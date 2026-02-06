/**
 * Utility: Debounce function to limit how often a function runs.
 * Professional touch for performance and UX.
 */
const debounce = (fn, delay = 500) => {
    let timeoutId;
    return (...args) => {
        if (timeoutId) clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(null, args), delay);
    };
};

/**
 * Validation Rules Configuration
 * 'Pythonic' approach: Change the data here to change the behavior of the app.
 */
const validationRules = {
    username: {
        required: true,
        min: 3,
        max: 15
    },
    email: {
        required: true,
        isEmail: true
    },
    password: {
        required: true,
        min: 6,
        max: 25
    },
    password2: {
        required: true,
        match: 'password'
    }
};

class FormValidator {
    constructor(formId, rules) {
        this.form = document.getElementById(formId);
        this.rules = rules;

        // Create a debounced version of our field validator
        this.debouncedValidate = debounce((input) => this.validateField(input), 400);

        this.init();
    }

    init() {
        // 1. Instant validation on Submit
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.validateAll();
        });

        // 2. Debounced validation on Input (Real-time)
        this.form.addEventListener('input', (e) => {
            this.debouncedValidate(e.target);
        });

        // 3. Instant validation on Blur (When user clicks away)
        this.form.addEventListener('blur', (e) => {
            this.validateField(e.target);
        }, true);
    }

    /**
     * The core engine: Validates a single input based on the config rules.
     */
    validateField(input) {
        const rules = this.rules[input.id];
        if (!rules) return;

        const value = input.value.trim();

        // Reset state
        this.showSuccess(input);

        // Rule: Required
        if (rules.required && !value) {
            return this.showError(input, `${this.getFieldName(input)} is required`);
        }

        // Rule: Min/Max Length
        if (rules.min && value.length < rules.min) {
            return this.showError(input, `${this.getFieldName(input)} must be at least ${rules.min} characters`);
        }
        if (rules.max && value.length > rules.max) {
            return this.showError(input, `${this.getFieldName(input)} must be less than ${rules.max} characters`);
        }

        // Rule: Email Regex
        if (rules.isEmail && !this.isValidEmail(value)) {
            return this.showError(input, 'Email is not valid');
        }

        // Rule: Field Matching (e.g., Password Confirmation)
        if (rules.match) {
            const targetInput = document.getElementById(rules.match);
            if (value !== targetInput.value) {
                return this.showError(input, 'Passwords do not match');
            }
        }
    }

    validateAll() {
        Object.keys(this.rules).forEach(id => {
            const input = document.getElementById(id);
            if (input) this.validateField(input);
        });
    }

    // --- UI Helpers ---

    showError(input, message) {
        const container = input.closest('.form-control');
        container.classList.remove('success');
        container.classList.add('error');

        const small = container.querySelector('small');
        small.textContent = message;

        // ARIA for Accessibility
        input.setAttribute('aria-invalid', 'true');
    }

    showSuccess(input) {
        const container = input.closest('.form-control');
        container.classList.remove('error');
        container.classList.add('success');
        input.setAttribute('aria-invalid', 'false');
    }

    // --- Logic Helpers ---

    isValidEmail(email) {
        const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email.toLowerCase());
    }

    getFieldName(input) {
        if (input.id === 'password2') return 'Confirmation';
        return input.id.charAt(0).toUpperCase() + input.id.slice(1);
    }
}

// Initialization
new FormValidator('form', validationRules);