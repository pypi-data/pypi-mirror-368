from enum import Enum
from typing import Optional, List

from espn_api_orm.consts import ESPNSportTypes
from espn_api_orm.generic.schema import BaseType
from espn_api_orm.season.api import ESPNSeasonAPI
from espn_api_orm.team.schema import Team


class ESPNTeamAPI(ESPNSeasonAPI):
    """
    ESPN Team API for retrieving sport information about a specific team.

    Attributes:

    Methods:
    """

    def __init__(self, sport: ESPNSportTypes, league: str, season: int, team_id: int):
        """
        Initialize ESPNTeamAPI.
        """
        super().__init__(sport, league, season)
        self.team_id = team_id

    def get_team(self) -> Team:
        res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/teams/{self.team_id}")
        if res is None:
            raise Exception(f'Invalid Season: {self.season} for {self.sport.value}/{self.league}')
        return Team(**res)

    def get_record(self, season_type=2):
        res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/types/{season_type}/teams/{self.team_id}/record")
        return res

    def get_depthchart(self):
        res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/teams/{self.team_id}/depthcharts")
        return res

    def get_roster(self):
        res = self.api_request(f"{self._base_url}/{self.sport.value}/{self.league}/teams/{self.team_id}/roster")
        return res

    def get_detailed_roster(self):
        res = self.api_request(f"{self._base_url}/{self.sport.value}/{self.league}/teams/{self.team_id}?enable=roster,projection,stats")
        return res

    def get_schedule(self):
        res = self.api_request(f"{self._base_url}/{self.sport.value}/{self.league}/teams/{self.team_id}/schedule?season={self.season}")
        return res

    def get_events(self):
        return self.get_values(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/teams/{self.team_id}/events")

    def get_injuries(self):
        res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/teams/{self.team_id}/injuries?limit=1000")
        return res

    def get_statistics(self, season_type=2):
        res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/types/{season_type}/teams/{self.team_id}/statistics")
        return res

    def get_past_performance(self, bet_provider_id, limit: int = 1000):
        res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/teams/{self.team_id}/odds/{bet_provider_id}/past-performances?limit={limit}")
        return res

    def get_projection(self):
        res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/teams/{self.team_id}/projection")
        return res

    def get_team_news(self):
        res = self.api_request(f"{self._base_url}/{self.sport.value}/{self.league}/news?team={self.team_id}")
        return res
