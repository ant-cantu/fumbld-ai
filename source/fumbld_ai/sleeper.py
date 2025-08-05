import requests, json, logging
from flask_login import current_user
from .models import SleeperLeague
from .utils import db
import pandas as pd
import os, re

logger = logging.getLogger("fumbld_logger")

season = "2024"

def get_sleeper_userid(username):
    try:
        response = requests.get(f'https://api.sleeper.app/v1/user/{username}')

        if response.status_code == 200:
            data = response.json()
            if data == "null":
                raise Exception("'get_sleeper_userid()': Sleeper username does not exist")
            
            if data['user_id']:
                return data['user_id']
        else:
            raise Exception(response.status_code)
    except Exception as e:
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: {e}")

def get_sleeper_leagues(user_id):
    try:
        query_sleeper = SleeperLeague.query.filter_by(user_id=current_user.id).all()

        if not query_sleeper:
            response = requests.get(f"https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{season}")
            league_data = []

            try: 
                if response.status_code == 200:
                    data = response.json()
                    if data == "null":
                        raise Exception("'get_sleeper_leagues()': League data does not exist.")
                    
                    for leagues in data:
                        if leagues['name'] and leagues['league_id']:
                            name = leagues['name']
                            league_id = leagues['league_id']
                            league_data.append({'id': league_id, 'league_name': name})

                    return league_data
                else:
                    raise Exception(response.status_code)
            except Exception as e:
                logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: {e}")
        else:
            league_list = []
            for league in query_sleeper:
                league_list.append({"id": league.sleeper_league_id, "league_name": league.sleeper_league_name})
            
            return league_list
    except Exception as e:
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: {e}")

def get_sleeper_league_setup(league_id):
    """
    Returns the leagues roster set up:
        Example: QB, WR, WR, RB, RB, FLEX, K, DST
    """
    response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}')
    league_setup = {}

    try:
        if response.status_code == 200:
            data = response.json()
            if data == "null":
                raise Exception("'get_sleeper_league_setup()': League data does not exist.")
            
            if data['roster_positions']:
                league_setup = data['roster_positions']
            
            return league_setup
        else:
            raise Exception(f"Received status code: {response.status_code} from the API endpoint.")
    except Exception as e:
        logger.error(e)

def get_sleeper_roster(league_id, username):
    starting_positions = get_sleeper_league_setup(league_id)

    query_team = SleeperLeague.query.filter_by(
        user_id=current_user.id,
        sleeper_league_id=league_id
    ).first()

    try:
        if query_team is None:
            response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/rosters')

            team_data = []
            if response.status_code == 200:
                data = response.json()
                if data == "null":
                    raise Exception("No roster data found for user")
                
                for owners in data:
                    if owners['owner_id'] == get_sleeper_userid(username):
                        players = owners['players']
                        starters = owners['starters']
                        
                        # file_path = 'c:\\Projects\\Python\\fumbld-ai\\source\\player_data.json'
                        file_path = '/app/player_data.json'
                        try:
                            with open(file_path, 'r') as file:
                                player_data = json.load(file)
                                for player_id, player_info in player_data.items():
                                    if player_id in players:
                                        name = player_info.get('full_name')
                                        position = player_info.get('position')

                                        # Projections
                                        projections = get_player_projection(remove_jr_suffix(name))
                                        if name == "Los Angeles":
                                            pp = "??"
                                        else:
                                            pp = projections.iloc[0]
                                            conf = projections.iloc[1]

                                        player_data = pd.read_csv("/app/nfl_stats/data/df_players_2024.csv")
                                        player_url = player_data[player_data['player_name'].str.contains(name, case=False, na=False)]
                                        if not player_url.empty:
                                            url = player_url['headshot_url'].iloc[0]

                                        if player_id in starters:
                                            team_data.append({'position': position, 'name': name, 'url': url, 'pp': pp, 'confidence': conf})
                                        else:
                                            team_data.append({'position': 'BN', 'name': name, 'url': url, 'pp': pp, 'confidence': conf})
                        except Exception as e:
                            logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: Unable to open Sleeper player data: {e}")

                # Sort by position before returning data
                position_priority = {'QB': 1, 'WR': 2, 'RB': 3, 'TE': 4, 'K': 5, 'DEF': 6, 'BN': 7}
                team_data = sorted(team_data, key=lambda x: position_priority.get(x['position'], 999)) 

                return team_data
            else:
                raise Exception(response.status_code)
        else:
            # If query found, return roster from database
            return query_team.sleeper_roster
    except Exception as e:
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: {e}")

def setup_sleeper(username):
    from .models import SleeperLeague

    # Query the users leagues
    query_leagues = SleeperLeague.query.filter_by(
        user_id=current_user.id
    ).all()

    if not query_leagues:
        sleeper_user_id = get_sleeper_userid(username)
        sleeper_leagues = get_sleeper_leagues(sleeper_user_id)

        league_ids = []
        league_names = []
        for leagues in sleeper_leagues:
            league_ids.append(leagues['id'])
            league_names.append(leagues['league_name'])

        for x in range(len(sleeper_leagues)):
            add_league = SleeperLeague(username, sleeper_user_id, league_ids[x], league_names[x], get_sleeper_league_setup(league_ids[x]) ,get_sleeper_roster(league_ids[x], username), user=current_user)
            
            try:
                db.session.add(add_league)
                db.session.commit()
                logger.info(f"User ID: {current_user.id} | Username: {current_user.username}: New Sleeper data saved to database for user")
            except Exception as e:
                db.session.rollback()
                logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: Unable to save Sleeper data to database: {e}")
    else:
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: League data already exist for user.")

def sleeper_refresh():
    try:
        sleeper_query = SleeperLeague.query.filter_by(user_id=current_user.id).first()
        sleeper_username = sleeper_query.sleeper_username

        SleeperLeague.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        setup_sleeper(sleeper_username)
    except Exception as e:
        db.session.rollback()
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: The database encountered an error during Sleeper refresh: {e}")

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
    # Match 'Jr', 'Jr.', 'jr', 'jr.', 'JR', 'JR.', etc., only if at the end
    # Allow for optional space/comma before Jr
    pattern = r'[ ,]*Jr\.?$'
    match = re.search(pattern, name, flags=re.IGNORECASE)
    print(f"Pattern match: {match}")
    result = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
    print(f"Result: '{result}'")
    return result