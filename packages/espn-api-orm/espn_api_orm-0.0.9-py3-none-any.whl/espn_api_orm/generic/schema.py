from typing import List, Optional, Any

from pydantic import BaseModel, Field
import datetime

class Ref(BaseModel):
    ref: str = Field(..., alias='$ref')

class BaseType(BaseModel):
    count: int
    pageIndex: int
    pageSize: int
    pageCount: int
    items: List[Ref]

class Types(BaseModel):
    ref: str = Field(..., alias='$ref')
    count: int
    pageIndex: int
    pageSize: int
    pageCount: int
    items: List[Any]

class Logo(BaseModel):
    href: str
    width: int
    height: int
    alt: str
    rel: List[str]
    lastUpdated: Optional[datetime.datetime] = None

class Link(BaseModel):
    language: Optional[str] = None
    rel: List[str]
    href: str
    text: Optional[str] = None
    shortText: Optional[str] = None
    isExternal: Optional[bool] = False
    isPremium: Optional[bool] = False

class Day(BaseModel):
    date: str
