# ai.py
from openai import OpenAI

# API Key
api_key = ""

# Create an object of OpenAPI and pass the API key to it
client = OpenAI(api_key=api_key)

# Determine which model to use
gpt_model = "gpt-4o" #"gpt-3.5-turbo"

fantasy_week = 17

# This will be passed from Yahoo/Sleeper API
users_roster = [
  {
    "name": "Jalen Hurts",
    "position": "QB",
    "team": "PHI",
    "status": "Healthy",
    "projected_points": 23.5,
    "opponent": "NYG",
    "opponent_rank_vs_position": 21,
    "start_percentage": 98.0,
    "starting": True
  },
  {
    "name": "Amon-Ra St. Brown",
    "position": "WR",
    "team": "DET",
    "status": "Healthy",
    "projected_points": 18.2,
    "opponent": "CHI",
    "opponent_rank_vs_position": 27,
    "start_percentage": 94.0,
    "starting": True
  },
  {
    "name": "Nico Collins",
    "position": "WR",
    "team": "HOU",
    "status": "Healthy",
    "projected_points": 15.1,
    "opponent": "TEN",
    "opponent_rank_vs_position": 25,
    "start_percentage": 76.0,
    "starting": True
  },
  {
    "name": "Breece Hall",
    "position": "RB",
    "team": "NYJ",
    "status": "Healthy",
    "projected_points": 16.3,
    "opponent": "MIA",
    "opponent_rank_vs_position": 14,
    "start_percentage": 89.0,
    "starting": True
  },
  {
    "name": "Kyren Williams",
    "position": "RB",
    "team": "LAR",
    "status": "Questionable",
    "projected_points": 14.0,
    "opponent": "ARI",
    "opponent_rank_vs_position": 31,
    "start_percentage": 83.4,
    "starting": True
  },
  {
    "name": "David Njoku",
    "position": "TE",
    "team": "CLE",
    "status": "Healthy",
    "projected_points": 9.2,
    "opponent": "CIN",
    "opponent_rank_vs_position": 12,
    "start_percentage": 41.2,
    "starting": True
  },
  {
    "name": "Christian Watson",
    "position": "FLEX (WR)",
    "team": "GB",
    "status": "Healthy",
    "projected_points": 12.1,
    "opponent": "MIN",
    "opponent_rank_vs_position": 22,
    "start_percentage": 55.0,
    "starting": True
  },
  {
    "name": "Cowboys",
    "position": "DEF",
    "team": "DAL",
    "status": "Healthy",
    "projected_points": 8.5,
    "opponent": "WAS",
    "opponent_rank_vs_position": "null",
    "start_percentage": 92.4,
    "starting": True
  },
  {
    "name": "Jake Elliott",
    "position": "K",
    "team": "PHI",
    "status": "Healthy",
    "projected_points": 7.8,
    "opponent": "NYG",
    "opponent_rank_vs_position": "null",
    "start_percentage": 78.2,
    "starting": True
  },
  # Bench
  {
    "name": "Jordan Addison",
    "position": "WR",
    "team": "MIN",
    "status": "Healthy",
    "projected_points": 11.3,
    "opponent": "GB",
    "opponent_rank_vs_position": 18,
    "start_percentage": 49.0,
    "starting": False
  },
  {
    "name": "Chuba Hubbard",
    "position": "RB",
    "team": "CAR",
    "status": "Healthy",
    "projected_points": 9.6,
    "opponent": "TB",
    "opponent_rank_vs_position": 6,
    "start_percentage": 28.1,
    "starting": False
  },
  {
    "name": "Tyler Boyd",
    "position": "WR",
    "team": "CIN",
    "status": "Healthy",
    "projected_points": 8.7,
    "opponent": "CLE",
    "opponent_rank_vs_position": 7,
    "start_percentage": 21.2,
    "starting": False
  },
  {
    "name": "Tyjae Spears",
    "position": "RB",
    "team": "TEN",
    "status": "Healthy",
    "projected_points": 8.2,
    "opponent": "HOU",
    "opponent_rank_vs_position": 13,
    "start_percentage": 24.3,
    "starting": False
  }
]

opp_roster = [
  {
    "name": "Josh Allen",
    "position": "QB",
    "team": "BUF",
    "status": "Healthy",
    "projected_points": 25.0,
    "opponent": "NE",
    "opponent_rank_vs_position": 10,
    "start_percentage": 99.3
  },
  {
    "name": "CeeDee Lamb",
    "position": "WR",
    "team": "DAL",
    "status": "Healthy",
    "projected_points": 17.9,
    "opponent": "WAS",
    "opponent_rank_vs_position": 29,
    "start_percentage": 97.0
  },
  {
    "name": "Chris Olave",
    "position": "WR",
    "team": "NO",
    "status": "Healthy",
    "projected_points": 13.5,
    "opponent": "TB",
    "opponent_rank_vs_position": 16,
    "start_percentage": 70.5
  },
  {
    "name": "Christian McCaffrey",
    "position": "RB",
    "team": "SF",
    "status": "Healthy",
    "projected_points": 21.3,
    "opponent": "SEA",
    "opponent_rank_vs_position": 9,
    "start_percentage": 100.0
  },
  {
    "name": "Aaron Jones",
    "position": "RB",
    "team": "GB",
    "status": "Questionable",
    "projected_points": 13.7,
    "opponent": "MIN",
    "opponent_rank_vs_position": 19,
    "start_percentage": 68.4
  },
  {
    "name": "Evan Engram",
    "position": "TE",
    "team": "JAX",
    "status": "Healthy",
    "projected_points": 10.4,
    "opponent": "ATL",
    "opponent_rank_vs_position": 15,
    "start_percentage": 58.6
  },
  {
    "name": "Michael Pittman Jr.",
    "position": "FLEX (WR)",
    "team": "IND",
    "status": "Healthy",
    "projected_points": 12.9,
    "opponent": "TEN",
    "opponent_rank_vs_position": 24,
    "start_percentage": 62.0
  },
  {
    "name": "Eagles",
    "position": "DEF",
    "team": "PHI",
    "status": "Healthy",
    "projected_points": 7.5,
    "opponent": "NYG",
    "opponent_rank_vs_position": "null",
    "start_percentage": 84.0
  },
  {
    "name": "Tyler Bass",
    "position": "K",
    "team": "BUF",
    "status": "Healthy",
    "projected_points": 8.1,
    "opponent": "NE",
    "opponent_rank_vs_position": "null",
    "start_percentage": 72.4
  }
]

fantasy_year = 2024

gpt_instructions = (
    f"You are a fantasy football expert. It is Week {fantasy_week}. "
    "Here is a list of dictionaries for the user's fantasy football roster with projections, injury statuses, and "
    "matchup data along with the user's opponent. Please review this information and recommend who to start and who to sit.\n"
    "The recommendation should be based on the projected points, opponent rank, and health of "
    "the player and the user's opponenets starters. If players are close, break the tie based on risk/reward.\n"
    "Do NOT make up or guess any information.\n\n"
    f"User's Team Roster:\n{users_roster}\n"
    f"User's Opponent Starters: \n{opp_roster}\n\n"
    "The starting lineup consist of one of each of these (exact position name to be used as dictionary keys): QB, WR, WR, RB, RB, TE, D/S/T, K, DEF\n\n"
    "Output your recommendations in this exact list of dictionaries format, no other input:\n"
    "---\n"
    "[\n"
    "{\"position\": \"player position\", \"name\": \"player name\"},\n"
    "{\"position\": \"player position\", \"name\": \"player name\"},\n"
    "etc..."
    "\n]\n"
    "---\n"
    "After the list of dictionaries output your reasoning in this exact format once again do NOT make up or guess:\n"
    "---\n"
    "Reason: 'reasoning here'"
    "---"
)

#def gpt_call(users_team, users_opp):
def gpt_call():
    gpt_input = [
        {
            "role": "user",
            #"content": f"User's Team: {users_team}\nUser's Opponent Starters: {users_opp}"
            "content": "Use instructions. For the D/S/T flex positon use 'D/S/T' as the dictionary key."
        }
    ]

    response = client.responses.create(
        model=gpt_model,
        instructions=gpt_instructions,
        input=gpt_input,
        temperature=0.4,
    )

    print(response.output_text)
    return response.output_text

if __name__ == "__main__":
    gpt_call()
