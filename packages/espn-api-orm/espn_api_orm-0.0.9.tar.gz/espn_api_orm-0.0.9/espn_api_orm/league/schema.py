import datetime
from typing import List, Optional, Any

from pydantic import BaseModel, Field

from espn_api_orm.generic.schema import Ref, Link, Logo
from espn_api_orm.season.schema import Season


class League(BaseModel):
    ref: str = Field(default=None, alias='$ref')
    id: int
    guid: Optional[str] = None
    uid: str
    name: str
    displayName: Optional[str] = None
    abbreviation: Optional[str] = None
    shortName: Optional[str] = None
    midsizeName: Optional[str] = None
    slug: Optional[str] = None
    isTournament: Optional[bool] = None
    season: Optional[Season]=None
    seasons: Optional[Ref] = None
    franchises: Optional[Ref] = None
    teams: Optional[Ref] = None
    group: Optional[Ref] = None
    groups: Optional[Ref] = None
    events: Optional[Ref] = None
    notes: Optional[Ref] = None
    rankings: Optional[Ref] = None
    links: Optional[List[Link]] = None
    logos: Optional[List[Logo]] = None
    powerIndexSeasons: Optional[Ref] = None
    calendar: Optional[Ref | Any] = None
    calendarType: Optional[str] = None
    calendarIsWhitelist: Optional[bool] = None
    calendarStartDate: Optional[datetime.datetime] = None
    calendarEndDate: Optional[datetime.datetime] = None
    transactions: Optional[Ref] = None
    gender: Optional[str] = None
