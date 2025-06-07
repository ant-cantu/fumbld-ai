# yahoo_fantasy.py
import yahoo_fantasy_api as yfa
from .utils import yahoo_api_connect

def get_roster(user):
    print(f"Pulling roster for user: {user.username}") # Debug

    # Connect to the yahoo API to make a request
    auth_handler = yahoo_api_connect()

    # Pass the authenticated object to the yahoo_fantasy_api Game class
    gm = yfa.Game(auth_handler, 'nfl')
    
    print(gm.game_id())
    roster_data = []
    # Example: Fetching data for a specific league
    # You would likely have the league_id stored or passed in for a multi-user app
    leagues = gm.league_ids()
    print(leagues)
    league = gm.to_league(leagues[0])
    team = league.to_team(league.team_key())
    roster = team.roster()

    for player in roster:
        if "name" in player:
            roster_data.append(player["name"])
            print(player["name"])

    return roster_data

    