##################################
# Scoreboard Classes
##################################

from typing import List, Optional, Any

from pydantic import BaseModel
import datetime

from espn_api_orm.generic.schema import Day, Logo, Link

## Day
from espn_api_orm.league.schema import League
from espn_api_orm.team.schema import TeamRef, Team
from espn_api_orm.venue.schema import Venue


class EventDate(BaseModel):
    date: datetime.datetime
    seasonType: int


## Events

class Athlete(BaseModel):
    id: int
    fullName: str
    displayName: str
    shortName: str
    links: List[Link]
    headshot: Optional[str] = None
    jersey: Optional[str] = None
    position: 'Position'
    team: TeamRef
    active: bool

    class Position(BaseModel):
        abbreviation: str


class CuratedRank(BaseModel):
    current: int


class Competitor(BaseModel):
    id: int
    uid: str
    type: str
    order: int
    homeAway: str
    winner: Optional[bool] = None
    team: Team
    score: str
    linescores: List['Linescore'] = []
    statistics: List['Statistic'] = []
    leaders: List['LeaderGroup'] = []
    curatedRank: Optional[CuratedRank] = None
    records: List['Record'] = []

    class Linescore(BaseModel):
        value: float

    class Statistic(BaseModel):
        name: str
        shortDisplayName: Optional[str] = None
        description: Optional[str] = None
        abbreviation: str
        displayValue: str
        value: Optional[float] = None

    class Record(BaseModel):
        name: str
        abbreviation: Optional[str] = None
        type: str
        summary: str

    class LeaderGroup(BaseModel):
        name: str
        displayName: str
        shortDisplayName: str
        abbreviation: str
        leaders: List['Leader'] = None

        class Leader(BaseModel):
            displayValue: str
            value: float
            athlete: 'Athlete'
            team: 'TeamRef'

class Competition(BaseModel):
    id: int
    uid: str
    date: datetime.datetime
    attendance: Optional[int] = None
    type: Optional['Type'] = None
    timeValid: bool
    neutralSite: bool
    conferenceCompetition: Optional[bool] = None
    playByPlayAvailable: bool
    recent: bool
    venue: Optional[Venue] = None
    competitors: List[Competitor]


    class Type(BaseModel):
        id: str
        abbreviation: str


class Event(BaseModel):
    id: int
    uid: str
    date: datetime.datetime
    name: str
    shortName: str
    season: 'Season'
    competitions: List[Competition]
    links: List['Link']
    status: 'Status'
    predictor: Optional[Any] = None
    powerIndex: Optional[Any] = None

    class Status(BaseModel):
        clock: Optional[float] = None
        displayClock: Optional[str] = None
        period: int
        type: 'Type'

        class Type(BaseModel):
            id: str
            name: str
            state: str
            completed: bool
            description: str
            detail: str
            shortDetail: str

    class Season(BaseModel):
        year: int
        type: int
        slug: str

