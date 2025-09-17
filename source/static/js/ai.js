const response = document.querySelector("#fumbld-response");    // AI Response Container
const mobileResponse = document.querySelector("#fumbld-mobile-response");
const insightBtn = document.querySelector("#insight-btn");  // AI Insight Button
const spinner = document.querySelector(".spinner-border");  // AI Loading Spinner
const aiTable = document.querySelector("#ai-players");      // Table for AI recommended players
const aiDiv = document.querySelector(".recommendations");   // Div container which holds AI table
const aiText = document.querySelector("#fumbld-head");
const defaultText = document.querySelector("#default-text");

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

/***** 1) FORMATTER: split on **, remove them, add spacing, bold the name *****/
function formatReason(reason) {
  // Split on ** and rebuild with spacing + bolded names; remove the ** markers.
  const parts = reason.split("**");
  let out = "";

  for (let i = 0; i < parts.length; i++) {
    if (i % 2 === 1) {
      // Inside former **...**
      const section = parts[i].trim();
      const m = section.match(/^(.*?):\s*(.+)$/); // "LABEL: Name"
      if (m) {
        const label = m[1].trim();
        const name = m[2].trim();
        out += `<br><br>${label}: <strong>${name}</strong>`;
      } else {
        // No label—just bold the whole section
        out += `<br><br><strong>${section}</strong>`;
      }
    } else {
      // Outside **...**, normal text
      const t = parts[i].trim();
      if (t) out += (out ? " " : "") + t; // single space separation
    }
  }

  return out.trim();
}

/***** 2) TYPEWRITER THAT PRESERVES HTML TAGS *****/
function typeHtml(targetEl, html, { speed = 20, onDone } = {}) {
  targetEl.innerHTML = "";

  // Parse HTML safely into a DOM tree
  const temp = document.createElement("div");
  temp.innerHTML = html;

  // Animate a text node’s content
  function typeText(textNode, fullText, idx, done) {
    if (idx < fullText.length) {
      textNode.textContent += fullText[idx];
      setTimeout(() => typeText(textNode, fullText, idx + 1, done), speed);
    } else {
      done && done();
    }
  }

  // Depth-first walk: clone elements, animate text nodes
  function walkAndAppend(srcNode, destParent, done) {
    const children = Array.from(srcNode.childNodes);
    let i = 0;

    function next() {
      if (i >= children.length) {
        done && done();
        return;
      }

      const child = children[i++];

      if (child.nodeType === Node.TEXT_NODE) {
        const textNode = document.createTextNode("");
        destParent.appendChild(textNode);
        typeText(textNode, child.textContent, 0, next);
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        const clone = child.cloneNode(false); // shallow
        destParent.appendChild(clone);
        walkAndAppend(child, clone, next);
      } else {
        // skip comments/others
        next();
      }
    }

    next();
  }

  // Build into a fragment for smoother rendering
  const frag = document.createDocumentFragment();
  walkAndAppend(temp, frag, () => {
    targetEl.dispatchEvent(new CustomEvent("typedone"));
    onDone && onDone();
  });
  targetEl.appendChild(frag);
}

/***** 3) UPDATED fetch_recommendation USING typeHtml *****/
function fetch_recommendation(provider, league_id) {
  if (league_id === "") {
    modal("Please select a league from the dashboard module.");
    return;
  }

  modal("Getting your recommendation 🤖");
  const modalSpinner = document.querySelector("#modal-spinner");
  modalSpinner.style.display = "block";
  modalCloseBtn.style.display = "none";

  // Clear the output box
  response.innerHTML = "";
  defaultText.innerHTML = "";

  fetch('/api/' + provider + '/leagues/' + league_id + '/recommendations')
    .then(response => response.json())
    .then(data => {
      if (data.error) {
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

      // Build the players table as you already do
      players.forEach(player => {
        const newRow = document.createElement('tr');
        const newHeadshot = document.createElement('td');
        const newPlayer = document.createElement('td');
        const newPos = document.createElement('td');
        const newProjP = document.createElement('td');
        const newConf = document.createElement('td');

        if (player.url === "🤖") {
          newHeadshot.textContent = player.url;
        } else {
          // Fix bad URLs
          if (player.url.startsWith("https://https://")) {
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
      const aiStarters = document.querySelector(".ai-starters");
      aiStarters.style.display = "none";

      // === NEW: format + type HTML safely ===
      const html = formatReason(reason);

      // Show the “Fumbld AI” line and target the typing span
      const defaultP = document.getElementById("default-text");
      if (defaultP) defaultP.style.display = "none";

      const head = document.getElementById("fumbld-head");
      if (head) head.style.display = "block";

      const target = document.getElementById("fumbld-response");

      // If you have a separate mobile target, swap it here.
      // Otherwise, we always use #fumbld-response.
      spinner.style.display = "block";
      typeHtml(target, html, {
        speed: 20,
        onDone: () => {
          spinner.style.display = "none";
        }
      });
    });
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
