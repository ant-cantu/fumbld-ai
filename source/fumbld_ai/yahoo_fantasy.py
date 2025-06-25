# yahoo_fantasy.py
import yahoo_fantasy_api as yfa
from .utils import yahoo_api_connect, db
from flask_login import current_user
from .models import YahooRoster

# Things TO-DO 6/24/25
# Limit API Calls
# Store user leagues in database?

def yahoo_get_leagues(year):
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

def yahoo_refresh_roster(league_id):
    try:
        # Delete the selected league (team)
        print(f"[DEBUG]: LeagueID: {league_id} has been deleted.")
        YahooRoster.query.filter_by(user_id=current_user.id, yahoo_league_id=league_id).delete()
        db.session.commit()

        # Call Yahoo API to get current roster
        yahoo_get_roster(league_id)
    except Exception as e:
        print(f"[ERROR]: The database encountered an error: {e}")


def yahoo_get_roster(league_id):
    starting_positions = {'QB', 'WR', 'RB', 'K', 'TE', 'W/R/T', 'DEF', 'BN'}

    query_team = YahooRoster.query.filter_by(
        user_id=current_user.id,
        yahoo_league_id=league_id
    ).first()

    if query_team is None:
        print("[DEBUG]: No team found, calling Yahoo API!")

        # Connect to the yahoo API to make a request
        auth_handler = yahoo_api_connect()

        # Pass the authenticated object to the yahoo_fantasy_api Game class
        gm = yfa.Game(auth_handler, 'nfl')
        
        league = gm.to_league(league_id)
        team = league.to_team(league.team_key())
        roster = team.roster()

        # Get player name and position
        team_data = []
        player_ids = []
        for player in roster:
            if player['selected_position'] in starting_positions:
                name = player['name']
                position = player['selected_position']
                player_id = player['player_id']
                team_data.append({'position': position, 'name': name})
                player_ids.append(player_id)
        
        
        # Get Player Headshot
        player_details = league.player_details(player_ids)
        headshot_urls = []
        for details in player_details:
            url = details['headshot']
            full_url = url['url']
            parsed_url = "https://" + full_url.split("/https://")[-1]
            headshot_urls.append(parsed_url)
        
        for player, url in zip(team_data, headshot_urls):
            player['url'] = url

        # Add team to users database
        new_roster = YahooRoster(league_id, team_data, user=current_user)

        try:
            db.session.add(new_roster)
            db.session.commit()
            print("[DEBUG]: Success Team Added To Database!")
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR]: {e}")
        
        return new_roster.yahoo_roster
    else:
        print("EXISTING TEAM FOUND IN DATABASE")
        return query_team.yahoo_roster

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
    
    team_data = []
    for player in opp_roster:
        if player['selected_position'] in starting_positions:
            name = player['name']
            position = player['selected_position']
            team_data.append({'position': position, 'name': name})

    return team_data