from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from espn_api_orm.generic.schema import Link


class Statistic(BaseModel):
    name: str
    shortDisplayName: Optional[str] = None
    description: Optional[str] = None
    abbreviation: str
    displayValue: str
    value: Optional[float] = None

class Athlete(BaseModel):
    id: int
    uid: Optional[str]
    guid: Optional[str]
    type: Optional[str]
    alternateIds: Optional[Dict[str, Any]]
    firstName: Optional[str]
    lastName: Optional[str]
    fullName: Optional[str]
    displayName: Optional[str]
    shortName: Optional[str]
    weight: Optional[float]
    displayWeight: Optional[str]
    height: Optional[float]
    displayHeight: Optional[str]
    age: Optional[int]
    dateOfBirth: Optional[str]
    debutYear: Optional[int]
    links: Optional[List[Link]]
    birthPlace: Optional[Dict[str, Any]]
    college: Optional[Dict[str, Any]]
    slug: Optional[str]
    headshot: Optional[Dict[str, Any]]
    jersey: Optional[str]
    position: Optional[Dict[str, Any]]
    linked: Optional[bool]
    #team: Optional[Dict[str, Any]]
    statistics: Optional[Dict[str, Any]]
    contracts: Optional[Dict[str, Any]]
    experience: Optional[Dict[str, Any]]
    collegeAthlete: Optional[Dict[str, Any]]
    active: Optional[bool] = False
    draft: Optional[Dict[str, Any]]
    status: Optional[Dict[str, Any]]
    statisticslog: Optional[Dict[str, Any]]

class AthleteGamelog(BaseModel):
    id: int
    games: Optional[List[Dict[str, Any]]]
    # Add more fields as needed from the gamelog endpoint

class AthleteNotes(BaseModel):
    id: int
    notes: Optional[List[Dict[str, Any]]]
    # Add more fields as needed from the notes endpoint

class AthleteProjections(BaseModel):
    id: int
    projections: Optional[List[Dict[str, Any]]]
    # Add more fields as needed from the projections endpoint

class AthleteSplits(BaseModel):
    id: int
    splits: Optional[List[Dict[str, Any]]]
    # Add more fields as needed from the splits endpoint

class AthleteStatistics(BaseModel):
    id: int
    statistics: Optional[List[Dict[str, Any]]]
    # Add more fields as needed from the statistics endpoint
class TeamLink(BaseModel):
    language: Optional[str]
    rel: Optional[List[str]]
    href: Optional[str]
    text: Optional[str]
    shortText: Optional[str]
    isExternal: Optional[bool]
    isPremium: Optional[bool]

class TeamHistory(BaseModel):
    id: str
    uid: str
    slug: str
    displayName: str
    logo: str
    seasons: str
    links: List[TeamLink]
    seasonCount: str
    isActive: bool

class AthleteBio(BaseModel):
    teamHistory: List[TeamHistory]
    id: int
    stats: Optional[List[Dict[str, Any]]]
