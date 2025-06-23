// Buttons
const dashboardBtn = document.querySelector("#dashboard");
const aiBtn = document.querySelector("#ai");
const matchupBtn = document.querySelector("#matchups");
const rankingBtn = document.querySelector("#rankings");
const settingsBtn = document.querySelector("#settings");

// Containers
const dashboard = document.querySelector(".dashboard-container");
const ai = document.querySelector(".ai-container");
const matchups = document.querySelector(".matchup-container");
const rankings = document.querySelector(".rankings-container");
const settings = document.querySelector(".settings-container");

function hideAllMenus() {
    dashboard.style.display = "none";
    ai.style.display = "none";
    matchups.style.display = "none";
    rankings.style.display = "none";
    settings.style.display = "none";
}

dashboardBtn.addEventListener("click", () => {
    hideAllMenus();
    dashboard.style.display = "flex";
});

aiBtn.addEventListener("click", () => {
    hideAllMenus();
    ai.style.display = "flex";
});

matchupBtn.addEventListener("click", () => {
    hideAllMenus();
    matchups.style.display = "flex";
});

rankingBtn.addEventListener("click", () => {
    hideAllMenus();
    rankings.style.display = "flex";
});

settingsBtn.addEventListener("click", () => {
    hideAllMenus();
    settings.style.display = "flex";
});



