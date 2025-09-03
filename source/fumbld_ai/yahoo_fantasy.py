# yahoo_fantasy.py
import yahoo_fantasy_api as yfa
from .utils import yahoo_api_connect, db
from flask_login import current_user
from .models import YahooLeague
import pandas as pd
import logging, os, re

season = 2025
logger = logging.getLogger("fumbld_logger")

def yahoo_set_leagues():
    years = [season] # The year we are pulling leagues from
    starting_positions = {'QB', 'WR', 'RB', 'K', 'TE', 'W/R/T', 'DEF', 'BN'}

    league_ids = []
    league_names = []
    league_teams = {}
    league_positions = {}

    # Query the users leagues
    query_leagues = YahooLeague.query.filter_by(
        user_id=current_user.id
    ).all()

    if not query_leagues:
        try:
            # Connect to the Yahoo API to make a request
            auth_handler = yahoo_api_connect()
        except Exception as e:
            logger.critical(f"There was an error connecting to the Yahoo! Sports API: {e}")

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

                # Initialize league_positions for this league
                league_positions[league] = []

                # Get positions played
                positions_played = lg.positions()
                for position_name, position_details in positions_played.items():
                    pos_starting = position_details.get('is_starting_position')
                    pos_amount = position_details.get('count')

                    if pos_starting == 1:
                        for x in range(pos_amount):
                            league_positions[league].append(position_name)

                starting_positions = league_positions[league]
                logger.log(f"****** Starting positions: {starting_positions} ******")

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
                # If player's position is one of the starting positons
                if player['selected_position'] in starting_positions:
                    name = player['name']
                    position = player['selected_position']

                    # Get player projections
                    if name == "Los Angeles":
                        pp = "??"
                        confidence = "??"
                    else:
                        projections = get_player_projection(remove_jr_suffix(name))
                        pp = projections.iloc[0]
                        confidence = projections.iloc[1]

                    # Replace W/R/T with D/S/T
                    if position == "W/R/T":
                        position = "D/S/T"
                    
                    # Used for headshot image
                    player_id = player['player_id']

                    # Append position and player names to 'team_data' list
                    team_data.append({
                        'position': position, 'name': name, 
                        'pp': pp, 
                        'confidence': confidence
                    })

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
        add_league = YahooLeague(league_ids[x], league_names[x], league_positions.get(league_ids[x]), league_teams[league_ids[x]], user=current_user)

        try:
            db.session.add(add_league)
            db.session.commit()
            logger.info(f"User ID: {current_user.id} | Username: {current_user.username}: Successfully added 'league_id: {league_ids[x]} to database from Yahoo! Sports API.")
        except Exception as e:
            db.session.rollback()
            logger.critical(f"User ID: {current_user.id} | Username: {current_user.username}: The application encountered an error saving Yahoo! Sports data to the database: {e}")

def yahoo_refresh():
    try:
        # Delete users league data from database
        YahooLeague.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()

        # Call Yahoo API to setup users leagues
        yahoo_set_leagues()
    except Exception as e:
        db.session.rollback()
        logger.critical(f"User ID: {current_user.id} | Username: {current_user.username}: The application encountered an error refresh league data from Yahoo! Sports: {e}")

def yahoo_get_league():
    """
    Retrieves each of the users league id and names from the database

    Returns:
        Returns league_id and league_name from database in a dictionary format
    """
    try:
        league_name = []
        # query_leagues = UserLeagues.query.filter_by(user_id=current_user.id).all()
        query_leagues = YahooLeague.query.filter_by(user_id=current_user.id).all()
        for league in query_leagues:
            league_name.append({"id": league.yahoo_league_id, "league_name": league.yahoo_league_name})

        return league_name
    except Exception as e:
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: Unable to read data from the database: {e}")
        return {"error": "Unable to read data from the database"}

def yahoo_get_roster(league_id):
    query_team = YahooLeague.query.filter_by(
        user_id=current_user.id,
        yahoo_league_id=league_id
    ).first()

    if query_team is None:
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: League ID: {league_id} does not exist for this user.")
        return {"error": "League selected does not exist"}
    else:
        return query_team.yahoo_roster

# This needs to be refactored
# Create a database to save this information to
def yahoo_get_opp_roster():
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

def get_player_projection(player_name):
    csv_path = os.path.join(os.path.dirname(__file__), "..", "df_projected_points_2024.csv")

    try:
        nfl_data = pd.read_csv(csv_path)
        player_data = nfl_data[nfl_data['player_name'].str.contains(player_name, case=False, na=False)]
        if not player_data.empty:
            return player_data[['projected_points', 'confidence']].iloc[0]
        else:
            return None
    except FileNotFoundError:
        # Add debugging info
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Projections file not found at {csv_path}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Script directory: {os.path.dirname(__file__)}")
        try:
            logger.error(f"Contents of parent directory: {os.listdir(os.path.dirname(os.path.dirname(__file__)))}")
        except:
            pass
        return None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error reading projections file: {e}")
        return None

# Fix player names with suffix  
def remove_jr_suffix(name):
    print(f"Input: '{name}' (repr: {repr(name)})")
    # Match 'Jr', 'Jr.', 'Sr', 'Sr.', 'jr', 'jr.', 'sr', 'sr.', 'JR', 'JR.', 'SR', 'SR.', etc., only if at the end
    # Allow for optional space/comma before Jr/Sr
    pattern = r'[ ,]*(Jr|Sr)\.?$'
    match = re.search(pattern, name, flags=re.IGNORECASE)
    print(f"Pattern match: {match}")
    result = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
    print(f"Result: '{result}'")
    return result