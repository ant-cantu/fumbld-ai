const response = document.querySelector("#ai-response");    // AI Response Container
const insightBtn = document.querySelector("#insight-btn");  // AI Insight Button
const spinner = document.querySelector(".spinner-border");  // AI Loading Spinner
const aiTable = document.querySelector("#ai-players");      // Table for AI recommended players

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

function fetch_recommendation(league_id) {
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
    aiTable.innerHTML = '';
    spinner.style.display = "block";

    fetch('/fetch/ai/recommendation?league-id=' + league_id)
        .then(response => response.json())
        .then(data => {
            const players = data.players;
            const reason = data.reason;

            players.forEach(player => {
                // Fix bad URLs
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

                aiTable.appendChild(newRow);
            });
            
            const reasonContainer = document.querySelector("#ai-response");
            reasonContainer.innerHTML += "<p><strong>Fumbld AI</strong>: ";
            //reasonContainer.innerHTML = '';
            //reasonContainer.innerHTML = `<p>${reason}</p>`;
            
            ai_response = reason;
            typeIt();
        });
}

function typeIt() {
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
        response.innerHTML += ai_response[charCount];
        charCount++;
        setTimeout(typeIt, 10);
    }
    else {
        response.innerHTML += "</p>";
        spinner.style.display = "none";
    }
}

// Insight button event handler
insightBtn.addEventListener("click", () => {
    fetch_recommendation(leagueMenu.value);
});