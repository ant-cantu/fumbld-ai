// Password reset button
const passResetBtn = document.querySelector("#passResetBtn");
const passResetForm = document.querySelector("#pass-reset-form");
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

function yahoo_refresh() {
    /**
     * Sends a request to refresh Yahoo data by calling the '/fetch/yahoo/refresh' endpoint.
     * Logs the response message to the console upon completion.
     *
     * @function
     * @returns {void}
     */
    //fetch('/fetch/yahoo/refresh')
    fetch('/api/yahoo/leagues/refresh', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            modal(data.success);
        } else {
            modal(data.error);
        }
        modalCloseBtn.style.display = "block";
    });
}

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

// League Refresh Button
refreshBtn.addEventListener("click", () => {
    modalCloseBtn.style.display = "none";
    modal("Refreshing Yahoo! Sports league data. Please wait...");
    yahoo_refresh();
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