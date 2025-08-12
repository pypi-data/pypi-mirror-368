import pytest
from espn_api_orm.athlete.api import ESPNAthleteAPI
from espn_api_orm.athlete.schema import Athlete, AthleteBio, AthleteEventLog, AthleteGamelog, AthleteNotes, AthleteProjections, AthleteSplits, AthleteStatistics

@pytest.fixture
def athlete_api():
    # Example: NFL, league 'nfl', season 2022, team 1, athlete 14876
    return ESPNAthleteAPI('football', 'nfl', 2022, 1, 14876)

def test_get_athletes(athlete_api):
    res = athlete_api.get_athletes(limit=10)
    assert isinstance(res, dict)
    assert 'items' in res or 'athletes' in res

def test_get_athlete(athlete_api):
    res = athlete_api.get_athlete()
    assert isinstance(res, dict)
    assert 'id' in res
    athlete = Athlete(**res)
    assert athlete.id == 14876

def test_get_bio(athlete_api):
    res = athlete_api.get_bio()
    assert isinstance(res, dict)
    assert 'id' in res
    AthleteBio(**res)

def test_get_eventlog(athlete_api):
    res = athlete_api.get_eventlog(year=2022)
    assert isinstance(res, dict)
    AthleteEventLog(**res)

def test_get_gamelog(athlete_api):
    res = athlete_api.get_gamelog()
    assert isinstance(res, dict)
    AthleteGamelog(**res)

def test_get_notes(athlete_api):
    res = athlete_api.get_notes(year=2021)
    assert isinstance(res, dict)
    AthleteNotes(**res)

def test_get_projections(athlete_api):
    res = athlete_api.get_projections(year=2021, season_type=2)
    assert isinstance(res, dict)
    AthleteProjections(**res)

def test_get_splits(athlete_api):
    res = athlete_api.get_splits()
    assert isinstance(res, dict)
    AthleteSplits(**res)

def test_get_statistics(athlete_api):
    res = athlete_api.get_statistics(year=2021, season_type=2)
    assert isinstance(res, dict)
    AthleteStatistics(**res)

def test_get_statisticslog(athlete_api):
    res = athlete_api.get_statisticslog()
    assert isinstance(res, dict)
    AthleteStatisticsLog(**res)

def test_get_stats(athlete_api):
    res = athlete_api.get_stats()
    assert isinstance(res, dict)
    AthleteStats(**res)
