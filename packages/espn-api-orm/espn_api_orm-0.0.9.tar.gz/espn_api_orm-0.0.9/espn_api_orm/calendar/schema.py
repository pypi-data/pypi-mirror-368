##################################
# Calendar Classes
##################################

from typing import List, Optional, Any

from pydantic import BaseModel, Field
import datetime

from espn_api_orm.consts import ESPNSportSeasonTypes
from espn_api_orm.generic.schema import Ref, BaseType
from espn_api_orm.season.schema import Season, SeasonType


class Calendar(BaseModel):
    ref: str = Field(..., alias='$ref')
    startDate: datetime.datetime
    endDate: datetime.datetime
    eventDate: Optional['EventDate'] = None
    type: Optional[SeasonType | str] = None
    types: Optional['BaseType'] = None
    season: Optional[Ref | Season] = None
    year: Optional[int] = None
    sections: Optional[List['SeasonSection']] = None
    displayName: Optional[str] = None
    rankings: Optional[Ref] = None
    futures: Optional[Ref] = None
    leaders: Optional[Ref] = None

    class EventDate(BaseModel):
        type: str
        dates: List[datetime.datetime]

    class SeasonSection(BaseModel):
        label: str
        detail: Optional[str] = None
        startDate: datetime.datetime
        endDate: datetime.datetime
        seasonType: Optional[Ref] = None


class CalendarDates(BaseModel):
    startDate: datetime.datetime
    endDate: datetime.datetime
    dates: List[datetime.datetime]
    seasonType: ESPNSportSeasonTypes
