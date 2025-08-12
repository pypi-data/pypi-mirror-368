import pytest

from espn_api_orm.calendar.api import ESPNCalendarAPI
from espn_api_orm.consts import ESPNSportTypes, ESPNSportSeasonTypes
from espn_api_orm.generic.api import ESPNBaseAPI
from espn_api_orm.sport.api import ESPNSportAPI
from espn_api_orm.league.api import ESPNLeagueAPI
from espn_api_orm.season.api import ESPNSeasonAPI

@pytest.fixture
def league_api():
    sport_string ='basketball'
    sport = ESPNSportTypes(sport_string)
    league_string = 'mens-college-basketball'
    return ESPNLeagueAPI(sport, league_string)


@pytest.fixture
def seasons(league_api):
    seasons_list = league_api.get_seasons(return_values=True)
    seasons = []
    for season in seasons_list:
        seasons.append(season)
    return seasons


@pytest.fixture
def season_api(league_api, seasons):
    season = seasons[0]
    return ESPNSeasonAPI(league_api.sport, league_api.league, season)


@pytest.fixture
def calendar_api(season_api):
    season_types = season_api.get_valid_types(return_values=True)
    assert len(season_types) > 0
    return ESPNCalendarAPI(season_api.sport, season_api.league, season_api.season)

def test_get_league(league_api):
    league = league_api.get_league()
    assert league is not None
    assert league.id is not None


def test_calendar(season_api, calendar_api):
    season = season_api.get_season()
    assert season is not None
    assert season.startDate is not None
    assert season.type is not None

    season_types = season_api.get_valid_types(return_values=True)
    calendar_sections = calendar_api.get_calendar_sections(season_types)
    assert calendar_sections is not None
    assert len(calendar_sections) > 0

    weeks = {}
    for season_type in season_types:
        weeks[season_type] = calendar_api.get_weeks(ESPNSportSeasonTypes(season_type))
    assert weeks is not None
    assert len(weeks) > 0

