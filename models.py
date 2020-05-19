import uuid
from typing import Dict
from pydantic import BaseModel


class Aggregate(BaseModel):
    uuid: uuid.UUID
    version: int


class Event(BaseModel):
    uuid: uuid.UUID
    aggregate_uuid: uuid.UUID
    name: str
    data: Dict
