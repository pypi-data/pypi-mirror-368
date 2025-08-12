from typing import Optional, List

from espn_api_orm.generic.api import ESPNBaseAPI
from espn_api_orm.consts import ESPNSportTypes, ESPNSportSeasonTypes
from espn_api_orm.league.api import ESPNLeagueAPI
from espn_api_orm.scoreboard.schema import Scoreboard, Event



class ESPNScoreboardAPI(ESPNLeagueAPI):
    """
    ESPN Scoreboard API for retrieving sports events information.

    Attributes:
        SCHEMA (dict): Dictionary defining the data schema for events.

    Methods:
        get_scoreboard(sport, dates, limit=1000, groups=None): Retrieve scoreboard data for a specific sport.
        get_events(sport, dates, limit=1000, groups=None): Retrieve events data for a specific sport.

    """

    def __init__(self, sport: ESPNSportTypes, league: str):
        """
        Initialize ESPNScoreboardAPI.
        """
        super().__init__(sport, league)

    def get_scoreboard(self, dates, season_type: ESPNSportSeasonTypes=None, week:int=None, limit:int=1000, groups=None) -> Optional[Scoreboard]:
        """
        Retrieve scoreboard data for a specific sport.

        Args:
            season_type (ESPNSportSeasonTypes): Type of sport season.
            dates: Dates for events.
            limit (int): Limit of events to retrieve.
            groups: Groups for events.

        Returns:
            dict: API response containing scoreboard data.
        """
        url = f"{self._base_url}/{self.sport.value}/{self.league}/scoreboard?dates={dates}&limit={limit}"
        if groups is not None:
            url = f"{url}&groups={groups}"
        if season_type is not None:
            url = f"{url}&seasontype={season_type}"
        if week is not None:
            url = f"{url}&week={week}"
        return Scoreboard(**self.api_request(url))
