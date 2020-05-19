from dataclasses import dataclass
from typing import Union, List


@dataclass(frozen=True)
class OrderCreated:
    user_id: int


@dataclass(frozen=True)
class StatusChanged:
    new_status: str


Event = Union[OrderCreated, StatusChanged]


@dataclass(frozen=True)
class EventStream:
    events: List[Event]
    version: int
