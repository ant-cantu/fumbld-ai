# yahoo_fantasy.py
import yahoo_fantasy_api as yfa
from .utils import yahoo_api_connect

def get_roster(user):
    print(f"Pulling roster for user: {user.username}") # Debug

    starting_positions = {'QB', 'WR', 'RB', 'K', 'TE', 'W/R/T', 'DEF'}

    # Connect to the yahoo API to make a request
    auth_handler = yahoo_api_connect()

    # Pass the authenticated object to the yahoo_fantasy_api Game class
    gm = yfa.Game(auth_handler, 'nfl')
    
    team_data = []
    # Example: Fetching data for a specific league
    # You would likely have the league_id stored or passed in for a multi-user app
    leagues = gm.league_ids()
    print(leagues)
    league = gm.to_league(leagues[0])
    team = league.to_team(league.team_key())
    roster = team.roster()

    team_data = []
    for player in roster:
        if player['selected_position'] in starting_positions:
            name = player['name']
            position = player['selected_position']
            team_data.append({'position': position, 'name': name})

    return team_data

def get_opp_roster(user):
    print(f"Pulling opponents roster for user: {user.username}") # Debug

    starting_positions = {'QB', 'WR', 'RB', 'K', 'TE', 'W/R/T', 'DEF'}
    auth_handler = yahoo_api_connect()

    gm = yfa.Game(auth_handler, 'nfl')
    leagues = gm.league_ids()
    league = gm.to_league(leagues[0])
    team = league.to_team(league.team_key())
    opp = team.matchup(league.current_week())
    opp_team = league.to_team(opp)
    opp_roster = opp_team.roster()
    #print(opp_roster)
    #opp_roster_data = []
    
    team_data = []
    for player in opp_roster:
        if player['selected_position'] in starting_positions:
            name = player['name']
            position = player['selected_position']
            team_data.append({'position': position, 'name': name})

    return team_data