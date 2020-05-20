from uuid import UUID
from typing import Dict
from pydantic import BaseModel


class Aggregate(BaseModel):
    uuid: UUID
    version: int


class Event(BaseModel):
    uuid: UUID
    aggregate_uuid: UUID
    name: str
    data: Dict
