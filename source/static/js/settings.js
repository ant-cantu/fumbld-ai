// Password reset button
const passResetBtn = document.querySelector("#passResetBtn");
const passResetForm = document.querySelector("#pass-reset-form");

function yahoo_refresh() {
    /**
     * Sends a request to refresh Yahoo data by calling the '/fetch/yahoo/refresh' endpoint.
     * Logs the response message to the console upon completion.
     *
     * @function
     * @returns {void}
     */
    fetch('/fetch/yahoo/refresh')
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

    fetch("/functions/changepassword", {
        method: "POST",
        body: form
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            console.log(data.success);
            modal(data.success)
            passResetForm.reset();
        } else {
            console.log(data.error);
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