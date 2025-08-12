from espn_api_orm.calendar.schema import Calendar, CalendarDates
from espn_api_orm.consts import ESPNSportTypes, ESPNSportSeasonTypes, ESPNCalendarTypes
from espn_api_orm.generic.schema import BaseType
from espn_api_orm.season.api import ESPNSeasonAPI
from typing import List

class ESPNCalendarAPI(ESPNSeasonAPI):
    """
    ESPN Calendar API for retrieving sports calendar information.

    Methods:
    - get_calendar
    - get_calendar_dates
    """

    def __init__(self, sport: ESPNSportTypes, league: str, season: int):
        """
        Initialize ESPNScoreboardAPI.
        """
        super().__init__(sport, league, season)

    def get_calendar(self, season_type: ESPNSportSeasonTypes | int = None, calendar_type: ESPNCalendarTypes = ESPNCalendarTypes.ONDAYS, limit=1000):
        season_type = ESPNSportSeasonTypes(season_type) if type(season_type) is int else season_type
        url = f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}"
        if season_type is not None:
            url = f"{url}/types/{season_type.value}"
            if calendar_type is not None:
                url = f"{url}/calendar/{calendar_type.value}"
        if '?limit=' not in url:
            url = f"{url}?limit={limit}"
        return Calendar(**self.api_request(url))

    def get_weeks(self, season_type: ESPNSportSeasonTypes | int, detailed=False):
        season_type = ESPNSportSeasonTypes(season_type) if type(season_type) is int else season_type
        weeks = self.get_values(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/types/{season_type.value}/weeks?limit=1000")
        if not detailed:
            return weeks
        detail_weeks = []
        for week in weeks:
            res = self.api_request(f"{self._core_url}/{self.sport.value}/leagues/{self.league}/seasons/{self.season}/types/{season_type.value}/weeks/{week}")
            detail_weeks.append(res)
        return detail_weeks

    def get_calendar_sections(self, season_types: List[int], limit=1000):
        if 2 in season_types:
            season_types = [2, 3]
        else:
            season_types = [1]
        dates = []
        for season_type in season_types:
            calendar_obj = self.get_calendar(ESPNSportSeasonTypes(season_type), limit=limit)
            dates.append(CalendarDates(**
                {
                    'startDate': calendar_obj.startDate,
                    'endDate': calendar_obj.endDate,
                    'dates': calendar_obj.eventDate.dates,
                    'seasonType': ESPNSportSeasonTypes(season_type)
                }
            ))
        return dates

