from typing import List, Optional, Any

from pydantic import BaseModel, Field
import datetime

from espn_api_orm.generic.schema import Ref


class SeasonType(BaseModel):
    ref: str = Field(default=None, alias='$ref')
    id: str
    type: Optional[int] = None
    name: str
    abbreviation: str
    year: Optional[int] = None
    startDate: Optional[datetime.datetime] = None
    endDate: Optional[datetime.datetime] = None
    hasGroups: Optional[bool] = None
    hasStandings: Optional[bool] = None
    hasLegs: Optional[bool] = None
    groups: Optional[Ref] = None
    week: Optional['Week'] = None
    weeks: Optional[Ref] = None
    leaders: Optional[Ref] = None
    slug: Optional[str] = None

    class Week(BaseModel):
        ref: str = Field(default=None, alias='$ref')
        number: int
        startDate: datetime.datetime
        endDate: datetime.datetime
        text: str
        rankings: Optional[Ref] = None


class Season(BaseModel):
    ref: str = Field(default=None, alias='$ref')
    year: Optional[int] = None
    startDate: datetime.datetime
    endDate: datetime.datetime
    displayName: Optional[str] = None
    type: Optional[SeasonType | str] = None
    types: Optional['Types'] = None
    rankings: Optional[Ref] = None
    powerIndexes: Optional[Ref] = None
    powerIndexLeaders: Optional[Ref] = None
    athletes: Optional[Ref] = None
    futures: Optional[Ref] = None
    leaders: Optional[Ref] = None

    class Types(BaseModel):
        ref: str = Field(default=None, alias='$ref')
        count: int
        pageIndex: int
        pageSize: int
        pageCount: int
        items: List[SeasonType]

