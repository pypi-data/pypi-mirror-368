from espn_api_orm.athlete.schema import Athlete
from espn_api_orm.team.api import ESPNTeamAPI
from typing import Optional, Dict, Any

class ESPNAthleteAPI(ESPNTeamAPI):
    """
    ESPN Athlete API for retrieving athlete information and stats.
    Inherits from ESPNTeamAPI for dynamic sport/league/season/team referencing.
    """
    def __init__(self, sport: str, league: str, season: int, team_id: int, athlete_id: Optional[int] = None):
        super().__init__(sport, league, season, team_id)
        self.athlete_id = athlete_id

    def get_athlete(self, athlete_id: Optional[int] = None):
        aid = athlete_id or self.athlete_id
        url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/athletes/{aid}"
        res = self.api_request(url)
        return Athlete(**res)

    def get_eventlog(self, year: Optional[int] = None, athlete_id: Optional[int] = None) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        yr = year or self.season
        url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{yr}/athletes/{aid}/eventlog"
        return self.api_request(url)

    def get_gamelog(self, athlete_id: Optional[int] = None) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        url = f"{self._common_url}/{self.sport.value}/{self.league}/athletes/{aid}/gamelog"
        return self.api_request(url)

    def get_bio(self, athlete_id: Optional[int] = None) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        url = f"{self._common_url}/{self.sport.value}/{self.league}/athletes/{aid}/bio"
        return self.api_request(url)

    def get_statistics(self, year: Optional[int] = None, season_type: int = 2, athlete_id: Optional[int] = None, stat_id: int = 0) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        yr = year or self.season
        url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{yr}/types/{season_type}/athletes/{aid}/statistics/{stat_id}"
        return self.api_request(url)

    def get_splits(self, athlete_id: Optional[int] = None) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        url = f"{self._common_url}/{self.sport.value}/{self.league}/athletes/{aid}/splits"
        return self.api_request(url)

    def get_notes(self, year: Optional[int] = None, athlete_id: Optional[int] = None) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        yr = year or self.season
        url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{yr}/athletes/{aid}/notes"
        return self.api_request(url)

    def get_projections(self, year: Optional[int] = None, season_type: int = 2, athlete_id: Optional[int] = None) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        yr = year or self.season
        url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{yr}/types/{season_type}/athletes/{aid}/projections"
        return self.api_request(url)

    def get_statisticslog(self, athlete_id: Optional[int] = None) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/athletes/{aid}/statisticslog"
        return self.api_request(url)

    def get_overview(self, athlete_id: Optional[int] = None) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        url = f"{self._common_url}/{self.sport.value}/{self.league}/athletes/{aid}/overview"
        return self.api_request(url)

    def get_stats(self, athlete_id: Optional[int] = None) -> Dict[str, Any]:
        aid = athlete_id or self.athlete_id
        url = f"{self._common_url}/{self.sport.value}/{self.league}/athletes/{aid}/stats"
        return self.api_request(url)

if __name__ == "__main__":
    # Example usage
    api = ESPNAthleteAPI('football', 'nfl', 2022, 1, 14876)
    athlete = api.get_athlete()
    print(athlete)
    bio = api.get_bio()
    print(bio)