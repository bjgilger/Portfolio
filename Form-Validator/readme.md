## Form Validator

Simple client side form validation. Check requird, length, email and password match

## Project Specifications

- **Create form UI**
- **Modular Design:** The FormValidator class and the debounce function can be copy/pasted into any project and they will work.

- **Event Handling:** It uses Event Delegation (listening on the form) rather than attaching listeners to every input.

- **UX-First:** By using blur (instant) and input (debounced), the form feels intelligent. It doesn't nag the user while they type, but it corrects them immediately if they make a mistake.

- **Clean DOM Access:** It uses .closest() and .classList instead of brittle paths like .parentElement.parentElement.
