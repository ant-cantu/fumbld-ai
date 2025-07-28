// Password reset button
const passResetBtn = document.querySelector("#passResetBtn");
const passResetForm = document.querySelector("#pass-reset-form");
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Password reset form
passResetBtn.addEventListener("click", (e) => {
    e.preventDefault();
    const form = new FormData(passResetForm);

    //fetch("/functions/changepassword", {
    fetch('/api/users/me/password', {
        method: "POST",
        body: form
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            modal(data.success)
            passResetForm.reset();
        } else {
            modal(data.error);
            passResetForm.reset();
        }
    });
});

// Admin - generate registration code
const generateCodeBtn = document.querySelector("#generate-code");
generateCodeBtn.addEventListener("click", (e) => {
    e.preventDefault();

    fetch('/api/admin/generate-reg-code', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        return response.json()
    })
    .then(data => {
        if(data.success)
            modal(data.success);
        else
            modal(data.error);
    });
});