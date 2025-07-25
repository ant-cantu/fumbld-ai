import requests, json
from flask_login import current_user
from .models import SleeperLeague
from .utils import db

season = "2024"

def get_sleeper_userid(username):
    response = requests.get(f'https://api.sleeper.app/v1/user/{username}')

    if response.status_code == 200:
        data = response.json()
        if data['user_id']:
            return data['user_id']
    else:
        print({'error': response.status_code})

def get_sleeper_leagues(user_id):
    query_sleeper = SleeperLeague.query.filter_by(user_id=current_user.id).all()

    if not query_sleeper:
        response = requests.get(f"https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{season}")

        league_data = []
        if response.status_code == 200:
            data = response.json()
            for leagues in data:
                if leagues['name'] and leagues['league_id']:
                    name = leagues['name']
                    league_id = leagues['league_id']
                    league_data.append({'id': league_id, 'league_name': name})
            return league_data
        else:
            print({'error': response.status_code})
    else:
        print("Sleeper database entry found...")
        league_list = []
        for league in query_sleeper:
            league_list.append({"id": league.sleeper_league_id, "league_name": league.sleeper_league_name})
        
        return league_list

def get_sleeper_roster(league_id, username):
    query_team = SleeperLeague.query.filter_by(
        user_id=current_user.id,
        sleeper_league_id=league_id
    ).first()

    if query_team is None:
        response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/rosters')

        team_data = []
        if response.status_code == 200:
            data = response.json()
            for owners in data:
                if owners['owner_id'] == get_sleeper_userid(username):
                    players = owners['players']
                    starters = owners['starters']
                    
                    # file_path = 'c:\\Projects\\Python\\fumbld-ai\\source\\player_data.json'
                    file_path = '/app/player_data.json'
                    with open(file_path, 'r') as file:
                        player_data = json.load(file)
                        for player_id, player_info in player_data.items():
                            if player_id in players:
                                name = player_info.get('full_name')
                                position = player_info.get('position')

                                if player_id in starters:
                                    team_data.append({'position': position, 'name': name, 'url': '🤖'})
                                else:
                                    team_data.append({'position': 'BN', 'name': name, 'url': '🤖'})
                                
            return team_data
        else:
            print({'error': response.status_code})
    else:
        # If query found, return roster from database
        return query_team.sleeper_roster

def setup_sleeper(username):
    from .models import SleeperLeague

    # Query the users leagues
    query_leagues = SleeperLeague.query.filter_by(
        user_id=current_user.id
    ).all()

    if not query_leagues:
        print(username)
        sleeper_user_id = get_sleeper_userid(username)
        print(sleeper_user_id)
        sleeper_leagues = get_sleeper_leagues(sleeper_user_id)
        print(sleeper_leagues)

        league_ids = []
        league_names = []
        for leagues in sleeper_leagues:
            league_ids.append(leagues['id'])
            league_names.append(leagues['league_name'])

        db_list = []
        for x in range(len(sleeper_leagues)):
            add_league = SleeperLeague(username, sleeper_user_id, league_ids[x], league_names[x], get_sleeper_roster(league_ids[x], username), user=current_user)
            
            try:
                db.session.add(add_league)
                db.session.commit()
                print("[LOG][NOTICE]: New sleeper data saved to database")
            except Exception as e:
                db.session.rollback()
                print(f"[LOG][ERROR]: Unable to save data to database: {e}")
    else:
        print("[LOG][ERROR]: League already exist for user")

def sleeper_refresh():
    try:
        sleeper_query = SleeperLeague.query.filter_by(user_id=current_user.id).first()
        sleeper_username = sleeper_query.sleeper_username

        SleeperLeague.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        print(f"[LOG][DEBUG]: Sleeper leagues for User ID: '{current_user.id}' have been deleted.")

        setup_sleeper(sleeper_username)
    except Exception as e:
        db.session.rollback()
        print(f"[LOG][ERROR]: The database encountered an error: {e}")