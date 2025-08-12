import pytest
from espn_api_orm.consts import ESPNSportTypes
from espn_api_orm.generic.api import ESPNBaseAPI
from espn_api_orm.sport.api import ESPNSportAPI
from espn_api_orm.league.api import ESPNLeagueAPI


@pytest.fixture
def base_api():
    return ESPNBaseAPI()

@pytest.fixture
def sport_strings(base_api):
    return base_api.get_sports(return_values=True)

@pytest.fixture
def sports(sport_strings, base_api):
    sports = []
    for sport_string in sport_strings:
        sport = ESPNSportTypes(sport_string)
        sport_api = ESPNSportAPI(sport)
        sport_obj = sport_api.get_sport()
        league_strings = sport_api.get_leagues(return_values=True)
        leagues = []
        for league_string in league_strings:
            league_api = ESPNLeagueAPI(sport, league_string)
            league_obj = league_api.get_league()
            leagues.append({'league_name': league_string, 'league': league_obj})
        sports.append({'sport_name': sport.value, 'sport': sport_obj, 'league_names': league_strings, 'leagues': leagues})
    return sports

def test_sports(sports):
    assert len(sports) > 0
    assert all(sport['sport'] is not None for sport in sports)