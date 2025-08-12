import pytest

from espn_api_orm.team.api import ESPNTeamAPI


@pytest.fixture
def team_api():
    team_api = ESPNTeamAPI('football','nfl',2022,1)
    return team_api

def test_team(team_api):
    assert team_api.get_team() is not None

def test_record(team_api):
    assert team_api.get_record() is not None

def test_depthchart(team_api):
    assert team_api.get_depthchart() is not None

def test_roster(team_api):
    assert team_api.get_roster() is not None

def test_detailed_roster(team_api):
    assert team_api.get_detailed_roster() is not None

def test_schedule(team_api):
    assert team_api.get_schedule() is not None

def test_events(team_api):
    assert team_api.get_events() is not None

def test_injuries(team_api):
    assert team_api.get_injuries() is not None

def test_statistics(team_api):
    assert team_api.get_statistics() is not None

def test_past_performance(team_api):
    assert team_api.get_past_performance(58) is not None