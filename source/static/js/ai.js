const response = document.querySelector("#fumbld-response");    // AI Response Container
const mobileResponse = document.querySelector("#fumbld-mobile-response");
const insightBtn = document.querySelector("#insight-btn");  // AI Insight Button
const spinner = document.querySelector(".spinner-border");  // AI Loading Spinner
const aiTable = document.querySelector("#ai-players");      // Table for AI recommended players
const aiDiv = document.querySelector(".recommendations");   // Div container which holds AI table
const aiText = document.querySelector("#fumbld-head");

let charCount = 0;      // Character counter for AI response type effect
let ai_response = "";   // This is set with the response from OpenAI

// --- Used for testing, so we don't waste OpenAI credits ---
// const ai_response = `Sam Darnold is chosen as the starting QB due to Matthew Stafford's bench status and potential injury concerns. 
//                     Saquon Barkley and D'Andre Swift are the top RB options, both having strong projected points and favorable matchups. 
//                     Zay Flowers and Adam Thielen are the best available WRs, with Flowers offering upside and Thielen providing a steady target share. 
//                     Jonnu Smith is the only active TE, making him the default choice. James Conner is selected for the D/S/T position due to his 
//                     consistent workload and potential for touchdowns. Chase McLaughlin is the sole kicker, and the Los Angeles defense is the only 
//                     option available, making them the default choice. Cooper Kupp's bench status and potential injury concerns keep him out of the 
//                     starting lineup.`;

function fetch_recommendation(provider, league_id) {
    /**
    * Fetches AI player recommendations for a given league and updates the UI table and response area.
    *
    * @param {string|number} league_id - The unique identifier for the league to fetch recommendations for.
    *
    * This function:
    * - Clears the current AI recommendations table and displays a loading spinner.
    * - Sends a GET request to the server to retrieve recommended players and the reasoning.
    * - Fixes malformed player image URLs if necessary.
    * - Dynamically creates and appends table rows for each recommended player, including their headshot, name, and position.
    * - Updates the AI response container with the reasoning for the recommendations.
    * - Triggers a typing animation for the AI response.
    */
    if(league_id === "") {
        modal("Please select a league from the dashboard module.")
        return;
    }

    modal("Getting your recommendation 🤖");
    const modalSpinner = document.querySelector("#modal-spinner");
    modalSpinner.style.display = "block";
    modalCloseBtn.style.display = "none";

    // fetch('/fetch/ai/recommendation?league-id=' + league_id)
    fetch('/api/' + provider + '/leagues/' + league_id + '/recommendations')
        .then(response => {
            return response.json()
        })
        .then(data => {
            if(data.error) {
                modal(data.error);
                modalCloseBtn.style.display = "block";
                spinner.style.display = "none";
                return;
            }

            // Clear tables/text
            aiDiv.style.display = "none";
            response.innerHTML = "";
            aiTable.innerHTML = "";
            ai_response = "";
            charCount = 0;

            // Display success message and allow user to close modal
            modal("Time to get that win! 🏈🏆");
            spinner.style.display = "block";

            // Grab data from backend
            const players = data.players;
            const reason = data.reason;

            players.forEach(player => {
                const newRow = document.createElement('tr');
                const newHeadshot = document.createElement('td');
                const newPlayer = document.createElement('td');
                const newPos = document.createElement('td');
                const newProjP = document.createElement('td');
                const newConf = document.createElement('td');

                if(player.url === "🤖") {
                    newHeadshot.textContent = player.url;
                } else {
                    // Fix bad URLs
                    if(player.url.startsWith("https://https://")) {
                        player.url = player.url.replace("https://https://", "https://");
                    }

                    const headshotImg = document.createElement('img');
                    headshotImg.src = player.url;
                    headshotImg.alt = player.name + " headshot image.";
                    headshotImg.height = 50;
                    newHeadshot.appendChild(headshotImg);
                }

                newPlayer.textContent = player.name;
                newPos.textContent = player.position;
                newProjP.textContent = player.pp;
                newConf.textContent = player.confidence;

                newRow.appendChild(newHeadshot);
                newRow.appendChild(newPlayer);
                newRow.appendChild(newPos);
                newRow.appendChild(newProjP);
                newRow.appendChild(newConf);

                aiTable.appendChild(newRow);
            });
            
            aiDiv.style.display = "block";
            aiText.style.display = "block";
            modalSpinner.style.display = "none";
            modalCloseBtn.style.display = "block";

            // Hide starters table
            const aiStarters = document.querySelector(".ai-starters")
            aiStarters.style.display = "none";
            //const reasonContainer = document.querySelector("#ai-response");
            //reasonContainer.innerHTML += "<p><strong>Fumbld AI</strong>: ";
            //reasonContainer.innerHTML = '';
            //reasonContainer.innerHTML = `<p>${reason}</p>`;
            
            ai_response = reason;

            if(mobileInsightBtn.classList.contains("mobile-active")) {
                sheet.classList.add('open');
                mobileInsightBtn.style.height = "50px";
                mobileInsightBtn.style.width = "150px";
                mobileInsightBtn.style.fontSize = "1rem";
                const sheetBtn = document.querySelector("#openSheet");
                sheetBtn.style.display = "flex";

                // Change the content container to flex-start after fumbld button is pressed
                const aiModuleContent = document.querySelector(".ai-container #content");
                aiModuleContent.style.justifyContent = "flex-start";

                typeIt(mobileResponse);
            } else {
                typeIt(response);
            }
            //mobileInsightBtn.classList.add("ai-active");
            
        });
}

function typeIt(textContainer) {
    /**
    * Animates the display of the AI response by typing out each character one at a time.
    * Continues until the entire response has been displayed, then hides the spinner.
    * 
    * Assumes the existence of the following global variables:
    * - ai_response: {string} The full response text to display.
    * - charCount: {number} The current character index being displayed.
    * - response: {HTMLElement} The DOM element where the response is shown.
    * - spinner: {HTMLElement} The DOM element representing the loading spinner.
    */
    if (charCount < ai_response.length) {
        textContainer.innerHTML += ai_response[charCount];
        charCount++;
        setTimeout(() => typeIt(textContainer), 20);
    }
    else {
        spinner.style.display = "none";
    }
}

// Insight button event handler
insightBtn.addEventListener("click", () => {
    fetch_recommendation(serviceDropDown.value, leagueMenu.value);
});

const mobileInsightBtn = document.querySelector("#mobile-insight-btn");
mobileInsightBtn.addEventListener("click", () => {
    mobileInsightBtn.classList.add("mobile-active");
    fetch_recommendation(serviceDropDown.value, leagueMenu.value);
});