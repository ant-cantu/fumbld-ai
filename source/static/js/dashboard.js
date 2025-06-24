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

// --------------------------------------

const yearMenu = document.querySelector("#year");
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

function fetch_leagues(year) {
    // Make a call to our API, returns users leagues
    fetch('fetch/yahoo/leagues?year=' + year)
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

function fetch_roster(league_id) {
    // Clear table first
    startersTable.innerHTML = '';
    benchTable.innerHTML = '';

    fetch('/fetch/yahoo/roster?league-id=' + league_id)
        .then(response => response.json())
        .then(data => {
            data.forEach(player => {
                const newRow = document.createElement('tr');
                const newPlayer = document.createElement('td');
                const newPos = document.createElement('td');

                newPlayer.textContent = player.name;
                newPos.textContent = player.position;

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
    const selectedYear = yearMenu.value;
    fetch_leagues(selectedYear);
});

// Year drop down was changed
yearMenu.addEventListener("change", () => {
    const selectedYear = yearMenu.value;
    fetch_leagues(selectedYear);
});

refreshBtn.addEventListener("click", () => {
    const league_id = leagueMenu.value;
    if(league_id != '') {
        fetch_roster(league_id);
        return;
    }
    else
    {
        // Report an error to the user here
    }
    
});


