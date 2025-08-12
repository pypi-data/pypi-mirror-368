import datetime

from espn_api_orm.consts import ESPNSportTypes, FIRST_SEASON
from espn_api_orm.league.schema import League
from espn_api_orm.sport.api import ESPNSportAPI
from espn_api_orm.team.schema import Team


class ESPNLeagueAPI(ESPNSportAPI):
    """
    ESPN League API for retrieving sport information about a specific league.

    Attributes:

    Methods:
    """

    def __init__(self, sport: ESPNSportTypes, league: str):
        """
        Initialize ESPNSportAPI.
        """
        super().__init__(sport)
        self.league = league

    def get_league(self):
        return League(**self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}"))

    def get_seasons(self):
        return [i for i in self.get_values(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons?limit=200") if i > FIRST_SEASON]

    def get_first_season(self):
        return min(self.get_seasons())

    def get_current_season(self):
        return max(self.get_seasons())

    def is_active(self):
        try:
            season = self.get_current_season()
            reg_res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{season}")
            start_date = datetime.datetime.strptime(reg_res['startDate'], '%Y-%m-%dT%H:%MZ')
            end_date = datetime.datetime.strptime(reg_res['endDate'], '%Y-%m-%dT%H:%MZ')
            return start_date <= datetime.datetime.now() <= end_date
        except Exception as e:
            print(e)
            return False

    def get_franchises(self):
        return self.get_values(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/franchises?limit=1000")

    def get_team_ids(self):
        team_url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/teams"
        return self.get_values(team_url+"?limit=1000")

    def get_teams(self, ids):
        team_url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/teams"
        return [Team(**self.api_request(f"{team_url}/{team_id}")) for team_id in ids]

    def get_odds_providers(self):
        self.get_values(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/providers?limit=1000")

    def get_news(self, limit=1000):
        res = self.api_request(f"{self._base_url}/{self.sport.value}/{self.league}/news?limit={limit}")
        return res

    def get_venues(self):
        return self.get_values(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/venues?limit=1000")



