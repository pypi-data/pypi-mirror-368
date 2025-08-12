from typing import List, Optional, Any

from pydantic import BaseModel, Field
import datetime

from espn_api_orm.generic.schema import Day, Logo, Link

class Address(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None

class Venue(BaseModel):
    ref: Optional[str] = Field(default=None, alias='$ref')
    id: int
    fullName: Optional[str] = None
    address: Optional['Address'] = None
    capacity: Optional[int] = None
    grass: Optional[bool] = None
    indoor: Optional[bool] = None
    images: Optional[List[Logo]] = None