# ai.py
from flask import current_app
from openai import OpenAI
from google import genai
from google.genai import types

# Model we are using
gemini_model = "gemini-2.5-pro"
gpt_model = "gpt-4o"

instructions = (
    f"You are a fantasy football expert. Let's say it's Week 17 of the 2024 season. "
    #"Below are two rosters: the user's full team and their opponent's starters. "
    "Below is the user's full fantasy football roster."
    #"Each player includes projected points, opponent rank, and injury status.\n\n"
    #"Each player includes name (n), position (p), injury status (s), projected points (pp), opponent (o), opponent rank vs position (or)\n\n"
    "Each player includes name (n), position (p)\n\n"
    
    #f"User's Roster:\n{users_roster}\n"
    #f"Opponent Starters:\n{opp_roster}\n\n"

    "Choose 1 starter per position: QB, RB, RB, WR, WR, TE, D/S/T, K, DEF.\n"
    "The D/S/T position can be a WR, RB or TE. "
    "You can include bench players as well as long as their real position matches one of the available positions."
    # "Your recommendation of players the user should start is based on all player stats. Break ties by upside/risk"
    "Prioritize projected points, matchup rank, and health. Break ties by upside/risk.\n"
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
    "Reason: Your explanation here in 1 detailed paragraph."
)

def gemini_call(roster):
    client = genai.Client(api_key=current_app.config.get('GEMINI_API_KEY'))

    response = client.models.generate_content(
        model=gemini_model,
        contents=[f"Follow instructions. User's Roster:\n{roster}\n"],
        config=types.GenerateContentConfig(
            system_instruction=instructions,
            temperature=0.2
        )
    )
    return response.text

def gpt_call(roster):
    api_key = current_app.config.get("OPENAI_KEY")
    client = OpenAI(api_key=api_key)

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