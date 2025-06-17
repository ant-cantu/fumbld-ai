# ai.py
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# API Key
api_key = os.environ.get('OPENAI_KEY')

# Create an object of OpenAPI and pass the API key to it
client = OpenAI(api_key=api_key)

# Determine which model to use
gpt_model = "gpt-4o" #"gpt-3.5-turbo"

fantasy_week = 17

# This will be passed from Yahoo/Sleeper API
users_roster = [
  {"n": "Jalen Hurts", "p": "QB", "s": "Healthy", "pp": 23.5, "o": "NYG", "or": 21},
  {"n": "Amon-Ra St. Brown", "p": "WR", "s": "Healthy", "pp": 18.2, "o": "CHI", "or": 27},
  {"n": "Nico Collins", "p": "WR", "s": "Healthy", "pp": 15.1, "o": "TEN", "or": 25},
  {"n": "Breece Hall", "p": "RB", "s": "Healthy", "pp": 16.3, "o": "MIA", "or": 14},
  {"n": "Kyren Williams", "p": "RB", "s": "Questionable", "pp": 14.0, "o": "ARI", "or": 31},
  {"n": "David Njoku", "p": "TE", "s": "Healthy", "pp": 9.2, "o": "CIN", "or": 12},
  {"n": "Christian Watson", "p": "WR", "s": "Healthy", "pp": 12.1, "o": "MIN", "or": 22},
  {"n": "Cowboys", "p": "DEF", "s": "Healthy", "pp": 8.5, "o": "WAS", "or": "null"},
  {"n": "Jake Elliott", "p": "K", "s": "Healthy", "pp": 7.8, "o": "NYG", "or": "null"},
  # Bench
  {"n": "Jordan Addison", "p": "WR", "s": "Healthy", "pp": 11.3, "o": "GB", "or": 18},
  {"n": "Chuba Hubbard", "p": "RB", "s": "Healthy", "pp": 9.6, "o": "TB", "or": 6},
  {"n": "Tyler Boyd", "p": "WR", "s": "Healthy", "pp": 8.7, "o": "CLE", "or": 7},
  {"n": "Tyjae Spears", "p": "RB", "s": "Healthy", "pp": 8.2, "o": "HOU", "or": 13}
]

opp_roster = [
  {"n": "Josh Allen", "p": "QB", "s": "Healthy", "pp": 25.0, "o": "NE", "or": 10},
  {"n": "CeeDee Lamb", "p": "WR", "s": "Healthy", "pp": 17.9, "o": "WAS", "or": 29},
  {"n": "Chris Olave", "p": "WR", "s": "Healthy", "pp": 13.5, "o": "TB", "or": 16},
  {"n": "Christian McCaffrey", "p": "RB", "s": "Healthy", "pp": 21.3, "o": "SEA", "or": 9},
  {"n": "Aaron Jones", "p": "RB", "s": "Questionable", "pp": 13.7, "o": "MIN", "or": 19},
  {"n": "Evan Engram", "p": "TE", "s": "Healthy", "pp": 10.4, "o": "ATL", "or": 15},
  {"n": "Michael Pittman Jr.", "p": "FLEX (WR)", "s": "Healthy", "pp": 12.9, "o": "TEN", "or": 24},
  {"n": "Eagles", "p": "DEF", "s": "Healthy", "pp": 7.5, "o": "NYG", "or": "null"},
  {"n": "Tyler Bass", "p": "K", "s": "Healthy", "pp": 8.1, "o": "NE", "or": "null"}
]

# Each player includes name (n), position (p), injury status (s), projected points (pp), opponent (o), opponent rank vs position (or)
fantasy_year = 2024

# gpt_instructions = (
#     f"You are a fantasy football expert. It is Week {fantasy_week}. "
#     "Here is a list of dictionaries for the user's fantasy football roster with projections, injury statuses, and "
#     "matchup data along with the user's opponent. Please review this information and recommend who to start and who to sit.\n"
#     "The recommendation should be based on the projected points, opponent rank, and health of "
#     "the player and the user's opponenets starters. If players are close, break the tie based on risk/reward.\n\n"
#     f"User's Team Roster:\n{users_roster}\n"
#     f"User's Opponent Starters: \n{opp_roster}\n\n"
#     "The starting lineup consist of one of each of these (exact position name abrv to be used as dictionary keys): "
#     "QB = Quarterback, WR = Wide Receiver, WR = Wide Receiver, RB = Runningback, RB = Runningback, TE = Tight End, D/S/T = Flex, K = Kicker, DEF = Defensive Team\n"
#     # "Use a web search to verify your decision with expert consensus."
#     "do NOT make up or guess information.\n"
#     "Output your recommendations in this exact list of dictionaries format, no other input before:\n"
#     "---\n"
#     "[\n"
#     "{\"position\": \"player position\", \"name\": \"player name\"},\n"
#     "{\"position\": \"player position\", \"name\": \"player name\"},\n"
#     "etc..."
#     "\n]\n"
#     "---\n"
#     "After the list of dictionaries output your reasoning in a two to three paragraphs summarizing your decision reasoning.\n" 
#     "Use this exact format to return your reason:\n"
#     "---\n"
#     "Reason: 'reasoning here'"
#     "---"
# )

gpt_instructions = (
    f"You are a fantasy football expert. It's Week {fantasy_week}. "
    "Below are two rosters: the user's full team and their opponent's starters. "
    #"Each player includes projected points, opponent rank, and injury status.\n\n"
    "Each player includes name (n), position (p), injury status (s), projected points (pp), opponent (o), opponent rank vs position (or)\n\n"
    
    f"User's Roster:\n{users_roster}\n"
    f"Opponent Starters:\n{opp_roster}\n\n"

    "Choose 1 starter per position: QB, RB, RB, WR, WR, TE, D/S/T, K, DEF.\n"
    "The D/S/T position can be a WR, RB or TE. "
    # "Your recommendation of players the user should start is based on all player stats. Break ties by upside/risk"
    "Prioritize projected points, matchup rank, and health. Break ties by upside/risk.\n"
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
    "---\n"
    "Reason: 'Your explanation here in 1 detailed paragraph.'"
    "\n---"
)

#def gpt_call(users_team, users_opp):
def gpt_call():
    gpt_input = [
        {
            "role": "user",
            #"content": f"User's Team: {users_team}\nUser's Opponent Starters: {users_opp}"
            "content": "Follow instructions." # For the Flex positon use 'D/S/T' as the dictionary key. Return your reasoning as two to three paragraphs."
        }
    ]

    response = client.responses.create(
        model=gpt_model,
        instructions=gpt_instructions,
        input=gpt_input,
        # tools=[{"type": "web_search"}],
        temperature=0.2,
    )

    print(response.output_text)
    return response.output_text

if __name__ == "__main__":
    gpt_call()