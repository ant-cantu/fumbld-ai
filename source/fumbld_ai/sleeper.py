import requests, json

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
    response = requests.get(f"https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{season}")

    league_data = {'leagues': []}
    if response.status_code == 200:
        data = response.json()
        for leagues in data:
            if leagues['name'] and leagues['league_id']:
                name = leagues['name']
                league_id = leagues['league_id']
                league_data['leagues'].append({'id': league_id, 'league_name': name})

        # Add data to database from here
        return league_data
    else:
        print({'error': response.status_code})

def get_sleeper_roster(league_id):
    response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/rosters')

    team_data = []
    team_roster = {}
    if response.status_code == 200:
        data = response.json()
        for owners in data:
            if owners['owner_id'] == get_sleeper_userid("mrjland"):
                players = owners['players']
                starters = owners['starters']
                 
                with open('C:\\Users\\acantu\\Desktop\\player_data.json', 'r') as file:
                    player_data = json.load(file)
                    for player_id, player_info in player_data.items():
                        if player_id in players:
                            name = player_info.get('full_name')
                            position = player_info.get('position')

                            if player_id in starters:
                                team_data.append({'position': position, 'name': name})
                            else:
                                team_data.append({'position': 'BN', 'name': name})
                            
        team_roster[league_id] = team_data

        return team_roster
    # add league ids, league names, 
    else:
        print({'error': response.status_code})

sleeper_user_id = get_sleeper_userid('mrjland')

print("Sleeper Username: mrjland\n")
print(f"Sleeper Users ID: {sleeper_user_id} \n")

print("Sleeper User Leagues Data:")
sleeper_leagues = get_sleeper_leagues(sleeper_user_id)
print(f"{json.dumps(sleeper_leagues, indent=4)}\n\n")

league_ids = []
league_names = []
for leagues in sleeper_leagues['leagues']:
    print(f"Sleeper User League ID: {leagues['id']}")
    league_ids.append(leagues['id'])
    league_names.append(leagues['league_name'])

print("\n\n")

for leagues in sleeper_leagues['leagues']:
    print(f"Sleeper League ID: {leagues['id']}")
    print(f"Sleeper League Name: {leagues['league_name']}")
    print(f"League Roster: {json.dumps(get_sleeper_roster(leagues['id']), indent=4)}\n\n")

db_list = []
for x in range(len(sleeper_leagues['leagues'])):
    db_list.append([league_ids[x], league_names[x], get_sleeper_roster(league_ids[x])])
    print(f"Sleeper DB Test Input:\n {db_list[x]}")