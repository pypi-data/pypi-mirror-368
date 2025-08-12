from enum import Enum
from typing import Optional, List

from espn_api_orm.consts import ESPNSportTypes, ESPNSportSeasonTypes
from espn_api_orm.generic.schema import BaseType
from espn_api_orm.league.api import ESPNLeagueAPI
from espn_api_orm.season.schema import Season


class ESPNSeasonAPI(ESPNLeagueAPI):
    """
    ESPN League API for retrieving sport information about a specific league.

    Attributes:

    Methods:
    """

    def __init__(self, sport: ESPNSportTypes, league: str, season: int):
        """
        Initialize ESPNSportAPI.
        """
        super().__init__(sport, league)
        self.season: int = season

    def get_season(self) -> Season:
        res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}")
        if res is None:
            raise Exception(f'Invalid Season: {self.season} for {self.sport.value}/{self.league}')
        return Season(**res)

    def get_valid_types(self):
        return self.get_values(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/types")

    def get_groups(self, season_type: ESPNSportSeasonTypes | int):
        season_type = ESPNSportSeasonTypes(season_type) if type(season_type) is int else season_type
        return self.get_values(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/types/{season_type.value}/groups?limit=1000")


    def get_team_season_ids(self):
        return self.get_values(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/teams?limit=1000")





