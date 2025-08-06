import nfl_data_py as nfl

class NFLSchedule():
    """A class to handle NFL schedule data for a specific season and week.
    
    Attributes:
        season (int): The season year to pull NFL schedule from
        week (int): The week number in the season
        total_games (int): Total number of games scheduled for the week
        gameday (str): Date of the selected game
        weekday (str): Day of the week for the selected game
        gametime (str): Time when the selected game starts
        away_team (str): Name of the away team
        away_score (int): Score of the away team
        home_team (str): Name of the home team
        home_score (int): Score of the home team
    """
    def __init__(self, season, week):
        self.season = season
        self.week = week

        # Initialize game-specific attributes to None
        attrError = "You must initialize set_schedule(game=int:game of the week) before calling an attribute from NFLSchedule()"
        self.gameday = attrError
        self.weekday = attrError
        self.gametime = attrError
        self.away_team = attrError
        self.away_score = attrError
        self.home_team = attrError
        self.home_score = attrError

        # Get NFL Schedule
        df_schedule = nfl.import_schedules([self.season])

        # Assign schedule DF to a variable
        self._games_this_week = df_schedule[ df_schedule['week'] == self.week ]

        # Get total games for the week
        self.total_games = len(self._games_this_week)
        print(f"Total games this week: {self.total_games}")

        # Get total weeks played for the season
        for _, games in df_schedule.iterrows():
            total_weeks = 0
            if games['week'] > total_weeks:
                total_weeks = games['week']
        
        # Check if week arg is in-bounds
        if self.week <= 0 or self.week > total_weeks:
            raise Exception(f"Total weeks played this season: {total_weeks}, you are out of bounds. NFLSchedule(season={self.season}, week={self.week})")

    def set_schedule(self, game):
        """Set the current game details from the week's schedule.
        
        Args:
            game: Game number within the week (1-based indexing)
            
        Raises:
            Exception: If game number is out of bounds for the week
        """
        # Check if game arg is in-bounds
        if game <= 0 or game > self.total_games:
            raise Exception(f"Total games this week: {self.total_games}, you are out of bounds. NFLSchedule(season={self.season}, week={self.week})")
         
        selected_game = self._games_this_week.iloc[game - 1]
        
        self.gameday = selected_game['gameday']
        self.weekday = selected_game['weekday']
        self.gametime = selected_game['gametime']
        self.away_team = selected_game['away_team']
        self.away_score = selected_game['away_score']
        self.home_team = selected_game['home_team']
        self.home_score = selected_game['home_score'] 

    def list_games(self):
        game_num = 0
        for _, game in self._games_this_week.iterrows():
            game_num = game_num + 1

            gameday = game['gameday']
            weekday = game['weekday']
            gametime = game['gametime']
            away_team = game['away_team']
            home_team = game['home_team']

            print(f"Game: {game_num} | {gameday} {weekday} - {gametime} | {away_team} vs. {home_team}")

# schedule = NFLSchedule(season=2025, week=1)

# schedule.list_games()

# for games in range(schedule.total_games):
#     schedule.set_schedule(game=games+1)
#     print(f"Week {schedule.week} | {schedule.gameday} {schedule.weekday} - {schedule.gametime} | {schedule.away_team} vs. {schedule.home_team}")