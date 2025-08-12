##################################
# Scoreboard Classes
##################################

from typing import List, Optional, Any

from pydantic import BaseModel
import datetime

from espn_api_orm.event.schema import EventDate, Event
from espn_api_orm.generic.schema import Day, Logo, Link

## Day
from espn_api_orm.league.schema import League

class Scoreboard(BaseModel):
    leagues: List[League]
    groups: List[str] = None
    day: Optional[Day] = None
    eventsDate: Optional[EventDate] = None
    events: List[Event]
