from espn_api_orm.consts import ESPNSportTypes
from espn_api_orm.league.api import ESPNLeagueAPI
from espn_api_orm.venue.schema import Venue


class ESPNVenueAPI(ESPNLeagueAPI):
    """
    ESPN Venue API for retrieving sports venue information.

    Methods:
        get_venue(): Retrieve venue data for a specific sport.

    """

    def __init__(self, sport: ESPNSportTypes, league: str, venue_id: int):
        """
        Initialize ESPNVenueAPI.
        """
        sport: ESPNSportTypes = sport if isinstance(sport, ESPNSportTypes) else ESPNSportTypes(sport)
        super().__init__(sport, league)
        self.venue_id = venue_id

    def get_venue(self):
        url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/venues/{self.venue_id}"
        return Venue(**self.api_request(url))