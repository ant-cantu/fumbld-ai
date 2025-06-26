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

    dashboardBtn.classList.remove("active");
    aiBtn.classList.remove("active");
    matchupBtn.classList.remove("active");
    rankingBtn.classList.remove("active");
    settingsBtn.classList.remove("active");
}

dashboardBtn.addEventListener("click", () => {
    hideAllMenus();
    dashboard.style.display = "flex";
    // dashboardBtn.style.background = "#1F3C63";
    dashboardBtn.classList.add("active");
});

aiBtn.addEventListener("click", () => {
    hideAllMenus();
    ai.style.display = "flex";
    aiBtn.classList.add("active");
});

matchupBtn.addEventListener("click", () => {
    hideAllMenus();
    matchups.style.display = "flex";
    matchupBtn.classList.add("active");
});

rankingBtn.addEventListener("click", () => {
    hideAllMenus();
    rankings.style.display = "flex";
    rankingBtn.classList.add("active");
});

settingsBtn.addEventListener("click", () => {
    hideAllMenus();
    settings.style.display = "flex";
    settingsBtn.classList.add("active");
});

// --------------------------------------

const leagueMenu = document.querySelector("#leagues");
const refreshBtn = document.querySelector("#refresh");

// Roster Tables
const startersTable = document.querySelector("#starter-players");
const benchTable = document.querySelector("#bench-players");

function create_placeholder(status) {
    // Clear drop down
    leagueMenu.options.length = 0;
    const placeholder = document.createElement('option');
    placeholder.value = '';

    // Create a placeholder text
    if(status == "loading") 
        placeholder.textContent = "Loading...";
    else if(status == "complete")
        placeholder.textContent = "--Select an option--";

    leagueMenu.appendChild(placeholder);
}

function fetch_leagues() {
    // Make a call to our API, returns users leagues
    fetch('fetch/yahoo/leagues')
        .then(response => {
            create_placeholder("loading");
            return response.json();
        })
        .then(data => {
            create_placeholder("complete");

            data.forEach(league => {
                const option = document.createElement('option');
                option.value = league.id;
                option.textContent = league.league_name;
                leagueMenu.appendChild(option);
            });

            leagueMenu.selectedIndex = 1;
            fetch_roster(leagueMenu.value);
        })
}

function yahoo_refresh() {
    fetch('/fetch/yahoo/refresh')
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        });
};

function fetch_roster(league_id) {
    // Clear table first
    startersTable.innerHTML = '';
    benchTable.innerHTML = '';

    fetch('/fetch/yahoo/roster?league-id=' + league_id)
        .then(response => response.json())
        .then(data => {
            data.forEach(player => {
                if(player.url.startsWith("https://https://")) {
                    player.url = player.url.replace("https://https://", "https://");
                }

                const newRow = document.createElement('tr');
                const newHeadshot = document.createElement('td');
                const newPlayer = document.createElement('td');
                const newPos = document.createElement('td');

                const headshotImg = document.createElement('img');
                headshotImg.src = player.url;
                headshotImg.alt = player.name + " headshot image.";
                headshotImg.height = 50;
                newHeadshot.appendChild(headshotImg);

                newPlayer.textContent = player.name;
                newPos.textContent = player.position;

                newRow.appendChild(newHeadshot);
                newRow.appendChild(newPlayer);
                newRow.appendChild(newPos);

                if(player.position != 'BN')
                    startersTable.appendChild(newRow);
                else 
                    benchTable.appendChild(newRow);
            })
        });
}

// Page is finished loading
document.addEventListener('DOMContentLoaded', () => {
    fetch_leagues();
});

// League drop down is changed
leagueMenu.addEventListener("change", () => {
    const selectedLeague = leagueMenu.value;
    fetch_roster(selectedLeague);
})

refreshBtn.addEventListener("click", () => {
    yahoo_refresh(league_id);
});


