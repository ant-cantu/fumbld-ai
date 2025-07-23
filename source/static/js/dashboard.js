// Buttons
const dashboardBtn = document.querySelectorAll("#dashboard");
const aiBtn = document.querySelectorAll("#ai");
const matchupBtn = document.querySelectorAll("#matchups");
const rankingBtn = document.querySelectorAll("#rankings");
const settingsBtn = document.querySelectorAll("#settings");

// Containers
const dashboard = document.querySelector(".dashboard-container");
const ai = document.querySelector(".ai-container");
const matchups = document.querySelector(".matchup-container");
const rankings = document.querySelector(".rankings-container");
const settings = document.querySelector(".settings-container");

// Modal Container
const modalPopUp = document.querySelector(".modalPopUp");
const modalContent = document.querySelector("#modalContent");
const modalCloseBtn = document.querySelector("#modalClose");

function hideAllMenus() {
    dashboard.style.display = "none";
    ai.style.display = "none";
    matchups.style.display = "none";
    rankings.style.display = "none";
    settings.style.display = "none";

    dashboardBtn.forEach(button => { button.classList.remove("active") });
    aiBtn.forEach(button => { button.classList.remove("active") });
    matchupBtn.forEach(button => { button.classList.remove("active") });
    rankingBtn.forEach(button => { button.classList.remove("active") });
    settingsBtn.forEach(button => { button.classList.remove("active") });
}

dashboardBtn.forEach(button => {
    button.addEventListener("click", () => {
        hideAllMenus();
        dashboard.style.display = "flex";
        button.classList.add("active");
        navLinks.classList.toggle("show");
    });
})

aiBtn.forEach(button => {
    button.addEventListener("click", () => {
        hideAllMenus();
        ai.style.display = "flex";
        button.classList.add("active");
        navLinks.classList.toggle("show");
    });
});

matchupBtn.forEach(button => {
    button.addEventListener("click", () => {
        hideAllMenus();
        matchups.style.display = "flex";
        button.classList.add("active");
        navLinks.classList.toggle("show");
    });
});

rankingBtn.forEach(button => {
    button.addEventListener("click", () => {
        hideAllMenus();
        rankings.style.display = "flex";
        button.classList.add("active");
        navLinks.classList.toggle("show");
    });
});

settingsBtn.forEach(button => {
    button.addEventListener("click", () => {
        hideAllMenus();
        settings.style.display = "flex";
        button.classList.add("active");
        navLinks.classList.toggle("show");
    });
});

// const mobileNav = document.querySelector("#select-nav");
// mobileNav.addEventListener('change', () => {
//     hideAllMenus()
//     switch(mobileNav.selectedIndex) {
//         case 0: dashboard.style.display = "flex"; break;
//         case 1: ai.style.display = "flex"; break;
//         case 2: matchups.style.display = "flex"; break;
//         case 3: rankings.style.display = "flex"; break;
//         case 4: settings.style.display = "flex"; break;
//     }
// });

// --------------------------------------

const leagueMenu = document.querySelector("#leagues");
const refreshBtn = document.querySelector("#refresh");

// Roster Tables
const startersTable = document.querySelectorAll("#starter-players");
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

function fetch_leagues(provider) {
    // Make a call to our API, returns users leagues
    // fetch('fetch/yahoo/leagues')
    // <provider> = yahoo
    fetch('/api/' + provider + '/leagues')
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
            fetch_roster(provider, leagueMenu.value);
        });
}

function fetch_roster(provider, league_id) {
    // Clear table first
    startersTable.forEach(table => {
        table.innerHTML = '';
    });
    // startersTable.innerHTML = '';
    benchTable.innerHTML = '';

    // Clear tables/text
    aiDiv.style.display = "none";
    response.innerHTML = "";
    aiTable.innerHTML = "";
    aiText.style.display = "none";
    ai_response = "";
    charCount = 0;

    // fetch('/fetch/yahoo/roster?league-id=' + league_id)
    // fetch('/api/yahoo/leagues/' + league_id + '/roster')
    fetch('/api/' + provider + '/leagues/' + league_id + '/roster')
        .then(response => response.json())
        .then(data => {
            data.forEach(player => {

                // Fix bad URLs
                
                if(player.url.startsWith("https://https://")) {
                    player.url = player.url.replace("https://https://", "https://");
                }

                const newRow = document.createElement('tr');
                const newHeadshot = document.createElement('td');
                const newPlayer = document.createElement('td');
                const newPos = document.createElement('td');

                if(player.url === "🤖") {
                    newHeadshot.textContent = player.url;
                } else {
                    const headshotImg = document.createElement('img');
                    headshotImg.src = player.url;
                    headshotImg.alt = player.name + " headshot image.";
                    headshotImg.height = 50;
                    newHeadshot.appendChild(headshotImg);
                }

                newPlayer.textContent = player.name;
                newPos.textContent = player.position;

                newRow.appendChild(newHeadshot);
                newRow.appendChild(newPlayer);
                newRow.appendChild(newPos);

                if(player.position != 'BN') {
                    startersTable.forEach(table => {
                        table.appendChild(newRow.cloneNode(true));
                    });
                    // startersTable.appendChild(newRow);
                }
                else 
                    benchTable.appendChild(newRow);
            });
        });
}

// Page is finished loading
document.addEventListener('DOMContentLoaded', () => {
    //fetch_leagues();
    if(serviceDropDown.length === 0) return;

    for(let i = 0; i < serviceDropDown.length; i++) {
        if(serviceDropDown[i].value === "yahoo" || serviceDropDown[i].value === "sleeper") {
            serviceDropDown.selectedIndex = i;
            if(leagueMenu.length > 0) {
                leagueMenu.selectedIndex = 1;
            }
            fetch_leagues(serviceDropDown[i].value);
            break;
        }
    }
});

// League drop down is changed
leagueMenu.addEventListener("change", () => {
    const selectedProvider = serviceDropDown.value;
    const selectedLeague = leagueMenu.value;
    console.log("provider: " + selectedProvider);
    console.log("league: " + selectedLeague);
    fetch_roster(selectedProvider, selectedLeague);
});

const serviceDropDown = document.querySelector("#provider");
serviceDropDown.addEventListener("change", () => {
    if(serviceDropDown.value === "yahoo") {
        fetch_leagues("yahoo");
    } else if(serviceDropDown.value === "sleeper") {
        fetch_leagues("sleeper")
    } else if(serviceDropDown.value === "") {
        // Clear league menu dropdown
        leagueMenu.innerHTML = "";

        // Add a default option to league menu
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '--Select a league--';
        leagueMenu.appendChild(defaultOption);

        // Clear roster table
        fetch_roster('');
    }
});


// --- Dashboard Modal ---
//

// Message to pass to the modal
function modal(message) {
    modalContent.innerHTML = '';
    modalContent.textContent = message;
    modalPopUp.style.display = "flex";
}

// Close modal button
modalCloseBtn.addEventListener("click", () => {
    modalContent.innerHTML = '';
    modalPopUp.style.display = "none";
});

// --- Slide Sheet ---
const sheet = document.getElementById('bottomSheet');
const openBtn = document.getElementById('openSheet');
const closeBtn = document.getElementById('closeSheet');

openBtn.addEventListener('click', () => {
    sheet.classList.add('open');
});

closeBtn.addEventListener('click', () => {
    sheet.classList.remove('open');
});

// --- Hamburger menu ---
const hamburger = document.getElementById('hamburgerButton');
const navLinks = document.getElementById('navLinks');

hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('show');
});