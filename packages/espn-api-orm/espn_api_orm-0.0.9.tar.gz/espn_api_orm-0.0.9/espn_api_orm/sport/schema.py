from typing import List, Optional

from pydantic import BaseModel, Field

from espn_api_orm.generic.schema import Ref, Logo

class Sport(BaseModel):
    ref: str = Field(..., alias='$ref')
    id: int
    guid: Optional[str] = None
    uid: str
    name: str
    displayName: str
    slug: str
    leagues: Ref
    logos: List[Logo]