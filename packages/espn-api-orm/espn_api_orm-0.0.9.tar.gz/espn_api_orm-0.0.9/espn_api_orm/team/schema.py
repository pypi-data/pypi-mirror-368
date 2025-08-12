from typing import List, Optional, Any
from espn_api_orm.generic.schema import Ref, Link, Logo
from pydantic import BaseModel, Field

from espn_api_orm.venue.schema import Venue

class TeamRef(BaseModel):
    id: int

class Team(BaseModel):
    ref: Optional[str] = Field(default=None, alias='$ref')
    id: int
    guid: Optional[str] = None
    uid: str
    alternateIds : Optional[dict] = None
    slug: Optional[str] = None
    location: str
    name: Optional[str] = None
    nickname: Optional[str] = None
    abbreviation: Optional[str] = None
    displayName: Optional[str] = None
    shortDisplayName: Optional[str] = None
    color: Optional[str] = None
    alternateColor: Optional[str] = None
    isActive: bool
    isAllStar: Optional[bool] = None
    logo: Optional[str] = None
    logos: Optional[List[Logo]] = None
    links: Optional[List[Link]] = None
    record: Optional[Any] = None
    oddsRecords: Optional[Any] = None
    athletes: Optional[Any] = None
    groups: Optional[Any] = None
    ranks: Optional[Any] = None
    statistics: Optional[Any] = None
    leaders: Optional[Any] = None
    injuries: Optional[Any] = None
    notes: Optional[Any] = None
    againstTheSpreadRecords: Optional[Any] = None
    franchise: Optional[Any] = None
    events: Optional[Any] = None
    college: Optional[Any] = None
    venue: Optional[Venue] = None
    conferenceId: Optional[int] = None