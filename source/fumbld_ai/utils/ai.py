# ai.py
from flask import current_app
from openai import OpenAI
from google import genai
from google.genai import types
import logging, re, json
from collections import namedtuple

logger = logging.getLogger("fumbld_logger")

# Model we are using
gemini_model = "gemini-2.5-pro"
gpt_model = "gpt-4o"

# Season Setup
week = "17"
season = "2024"

GeminiResult = namedtuple('GeminiResult', ['roster', 'reason'])

def gemini_call(roster, positions):
    api_key = current_app.config.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    instructions = (
        f"You are a fantasy football expert. It's Week {week} of the {season} season. "
        #"Below are two rosters: the user's full team and their opponent's starters. "
        "Below is the user's full fantasy football roster."
        #"Each player includes projected points, opponent rank, and injury status.\n\n"
        #"Each player includes name (n), position (p), injury status (s), projected points (pp), opponent (o), opponent rank vs position (or)\n\n"
        "Each player includes name (n), position (p), projected points (pp)\n\n"
        
        #f"User's Roster:\n{users_roster}\n"
        #f"Opponent Starters:\n{opp_roster}\n\n"

        f"Choose 1 starter per position: {positions}.\n"
        "The D/S/T or FLEX position can be a WR, RB or TE. The SUPER_FLEX position can be a QB, WR, RB, or TE."
        "You can include bench players as well as long as their real position matches one of the available positions."
        "All positions must be filled and must be returned in the same order as the positions provided without the benched players."
        # "Your recommendation of players the user should start is based on all player stats. Break ties by upside/risk"
        "Prioritize projected points, matchup rank, and health. Break ties by upside/risk. Consider weather for game locations.\n"
        "Only compare players to the current week of the season. "
        "Do NOT makeup or guess information.\n\n"

        "Respond only in the format:\n"
        "---\n"
        "[\n"
        "{\"position\": \"QB\", \"name\": \"Player Name\"},\n"
        "{\"position\": \"RB\", \"name\": \"Player Name\"},\n"
        "...etc"
        "\n]\n"
        "---\n"
        "Then give reasoning:\n"
        "---\n\n"
        "Reason: Your explanation here in one detailed paragraph."
    )

    try:
        response = client.models.generate_content(
            model=gemini_model,
            contents=[f"Follow instructions. User's Roster:\n{roster}\n"],
            config=types.GenerateContentConfig(
                system_instruction=instructions,
                temperature=0.2
            )
        )

        # Parse the response
        text = response.text

        #  Extract the JSON block between --- markers in gpt response
        # --- three dashes in string
        # \s* match any whitespace
        # (\[.*?\]) match and capture a json style list inside of [ ]
        roster_match = re.search(r'---\n(\[.*?\])\n---', text, re.DOTALL)

        # Extract the reason text in gpt response
        # start search starting with reason:
        # \s* optional whitespace after reason
        # (.*) capture group that grabs everything after the optional whitespace
        reason_match = re.search(r'Reason: (.*)', text, re.DOTALL)

        if roster_match and reason_match:
            roster_json = json.loads(roster_match.group(1))
            reason_text = reason_match.group(1).strip()

            return GeminiResult(roster=roster_json, reason=reason_text)
        else:
            logger.critical(f"Failed to parse a response from Gemini: {text}")
            return GeminiResult(roster=None, reason=f"Failed to parse response from Gemini. Please submit a bug report.")
    except Exception as e:
        logger.critical(f"Gemini API call failed | details: {e}") 
        return {"error": "Gemini API call failed", "details": str(e)}

def gpt_call(roster):
    api_key = current_app.config.get("OPENAI_KEY")
    client = OpenAI(api_key=api_key)

    instructions = ""

    gpt_input = [
        {
            "role": "user",
            #"content": f"User's Team: {users_team}\nUser's Opponent Starters: {users_opp}"
            "content": f"Follow instructions. User's Roster:\n{roster}\n" # For the Flex positon use 'D/S/T' as the dictionary key. Return your reasoning as two to three paragraphs."
        }
    ]

    response = client.responses.create(
        model=gpt_model,
        instructions=instructions,
        input=gpt_input,
        # tools=[{"type": "web_search"}],
        temperature=0.2,
    )
    return response.output_text

# if __name__ == "__main__":
#     gpt_call()