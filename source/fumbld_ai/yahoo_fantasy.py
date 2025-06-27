# yahoo_fantasy.py
import yahoo_fantasy_api as yfa
from .utils import yahoo_api_connect, db
from flask_login import current_user
from .models import YahooLeague

def yahoo_set_leagues():
    years = [2024] # The year we are pulling leagues from
    starting_positions = {'QB', 'WR', 'RB', 'K', 'TE', 'W/R/T', 'DEF', 'BN'}

    league_ids = []
    league_names = []
    league_teams = {}

    # Query the users leagues
    query_leagues = YahooLeague.query.filter_by(
        user_id=current_user.id
    ).all()

    if not query_leagues:
        # Connect to the Yahoo API to make a request
        auth_handler = yahoo_api_connect()

        # Create an object of yahoo_fantasy_api
        gm = yfa.Game(auth_handler, 'nfl')

        # Generate a list of league ID's associated with the user
        for year in years:
            leagues = gm.league_ids(year=year)

            for league in leagues:
                # Add league id to list of league ids, used for rosters
                league_ids.append(league)

                # Retrieve league info by league ID
                lg = gm.to_league(league)

                # Retrieve league settings which includes the name of the league
                lg_info = lg.settings()

                # Add league name to the league names list, used for database entry
                league_names.append(lg_info['name'])
        
        # Get users rosters for each league and save all data to database
        for league_id in league_ids:
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

                    # Append player id to 'player_ids' list, used to get headshot image url
                    player_ids.append(player_id)
            
            # Get Player Headshot
            player_details = league.player_details(player_ids)
            headshot_urls = []
            for details in player_details:
                url = details['headshot']
                full_url = url['url']
                parsed_url = "https://" + full_url.split("/https://")[-1]
                headshot_urls.append(parsed_url)
            
            # Add headshot image url to 'team_data' dictionary
            # final outcome: {'position': position, 'name': name, 'url': url}
            for player, url in zip(team_data, headshot_urls):
                player['url'] = url

            league_teams[league_id] = team_data
    
    for x in range(len(league_ids)):
        add_league = YahooLeague(league_ids[x], league_names[x], league_teams[league_ids[x]], user=current_user)
        # print(f"[DEBUG TEAM DATA]\n\n{league_teams[league_ids[x]]}\n\n")

        try:
            db.session.add(add_league)
            db.session.commit()
            print(f"[LOG]: 'user_id: {current_user.id}' 'username: {current_user.username}' successfully added 'league_id: {league_ids[x]} to database.")
        except Exception as e:
            db.session.rollback()
            print(f"[LOG][ERROR]: Unable to save data to database: {e}")


def yahoo_refresh():
    try:
        # Delete users league data from database
        YahooLeague.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        print(f"[LOG][DEBUG]: 'User ID: {current_user.id}' leagues has been deleted.")

        # Call Yahoo API to setup users leagues
        yahoo_set_leagues()
    except Exception as e:
        db.session.rollback()
        print(f"[LOG][ERROR]: The database encountered an error: {e}")

def yahoo_get_league():
    """
    Retrieves each of the users league id and names from the database

    Returns:
        Returns league_id and league_name from database in a dictionary format
    """
    league_name = []
    # query_leagues = UserLeagues.query.filter_by(user_id=current_user.id).all()
    query_leagues = YahooLeague.query.filter_by(user_id=current_user.id).all()
    for league in query_leagues:
        league_name.append({"id": league.yahoo_league_id, "league_name": league.yahoo_league_name})

    return league_name

def yahoo_get_roster(league_id):
    query_team = YahooLeague.query.filter_by(
        user_id=current_user.id,
        yahoo_league_id=league_id
    ).first()

    if query_team is None:
        print(f"[ERROR]: League ID: {league_id} does not exist for User ID: {current_user.id}")
    else:
        return query_team.yahoo_roster

# This needs to be refactored
# Create a database to save this information to
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