from espn_api_orm.calendar.api import ESPNCalendarAPI
from espn_api_orm.consts import ESPNSportTypes, ESPNSportSeasonTypes
from espn_api_orm.generic.api import ESPNBaseAPI
from espn_api_orm.scoreboard.api import ESPNScoreboardAPI
from espn_api_orm.season.api import ESPNSeasonAPI

base_api = ESPNBaseAPI()
single_test = True
sport_string = 'basketball'
sport = ESPNSportTypes(sport_string)

league_string = 'mens-college-basketball'
season = 2024

season_api = ESPNSeasonAPI(sport, league_string, season)
season_obj = season_api.get_season()
team_ids = season_api.get_team_ids()

if not season_obj.type.hasStandings:
    print('Fail')
season_types = season_api.get_valid_types(return_values=True)
calendar_api = ESPNCalendarAPI(sport, league_string, season)
calendar_sections = calendar_api.get_calendar_sections(season_types)

scoreboard_api = ESPNScoreboardAPI(sport, league_string)
events = {}
for calendar_section in calendar_sections[0:1]:
    for date in calendar_section.dates[0:1]:
        string_date = date.strftime('%Y%m%d')
        event_objs = scoreboard_api.get_events(string_date)[0]
        events[string_date] = event_objs
print(events)