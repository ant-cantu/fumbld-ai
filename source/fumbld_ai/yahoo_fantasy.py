# yahoo_fantasy.py
import yahoo_fantasy_api as yfa
from .utils import yahoo_api_connect

def yahoo_get_leagues(year):
    """
    Retrieve a list of Yahoo Fantasy Football leagues for a given year associated with the authenticated user.
    Args:
        year (int): The year for which to retrieve the user's leagues.
    Returns:
        list of dict: A list of dictionaries, each containing the league 'id' and 'league_name'.
    Raises:
        Any exceptions raised by the Yahoo API connection or data retrieval.
    Example:
        leagues = yahoo_get_leagues(2023)
        # leagues -> [{'id': '12345', 'league_name': 'My Fantasy League'}, ...]
    """
    # Connect to the Yahoo API to make a request
    auth_handler = yahoo_api_connect()

    # Create an object of yahoo_fantasy_api
    gm = yfa.Game(auth_handler, 'nfl')

    # Generate a list of league ID's associated with the user
    leagues = gm.league_ids(year=year)

    league_name = []
    for league in leagues:
        # Retrieve league info by league ID
        lg = gm.to_league(league)

        # Retrieve league settings which includes the name of the league
        lg_info = lg.settings()

        # Append league name as a dictionary
        league_name.append({"id": league, "league_name": lg_info['name']})
    
    return league_name

def yahoo_get_roster(league_id):
    starting_positions = {'QB', 'WR', 'RB', 'K', 'TE', 'W/R/T', 'DEF', 'BN'}

    # Connect to the yahoo API to make a request
    auth_handler = yahoo_api_connect()

    # Pass the authenticated object to the yahoo_fantasy_api Game class
    gm = yfa.Game(auth_handler, 'nfl')
    
    # Generate a list of league ID's associated with the user
    #leagues = gm.league_ids()

    print(f"yahoo_get_roster(): {league_id}")

    league = gm.to_league(league_id)
    team = league.to_team(league.team_key())
    roster = team.roster()

    team_data = []
    for player in roster:
        if player['selected_position'] in starting_positions:
            name = player['name']
            position = player['selected_position']
            team_data.append({'position': position, 'name': name})

    return team_data

def yahoo_get_opp_roster(user):
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