from dataclasses import dataclass
from typing import Set, List, Union
from functools import singledispatchmethod


@dataclass(frozen=True)
class OrderCreated:
    user_id: int


@dataclass(frozen=True)
class StatusChanged:
    new_status: str


Event = Union[OrderCreated, StatusChanged]


class Order:
    def __init__(self, events: List[Event]):
        for event in events:
            self.apply(event)

        self.changes: List[Event] = []

    @singledispatchmethod
    def apply(self, event):
        raise ValueError("Unknown event!")

    @apply.register
    def apply_order_created(self, event: OrderCreated):
        self.user_id = event.user_id
        self.status = "new"

    @apply.register
    def apply_status_changed(self, event: StatusChanged):
        self.status = event.new_status

    def set_status(self, new_status: str):
        allowed_statuses: Set[str] = {"new", "paid", "confirmed", "shipped"}
        if new_status not in allowed_statuses:
            raise ValueError(f"{new_status} is not a correct status!")
        event = StatusChanged(new_status)
        self.apply(event)
        self.changes.append(event)

    @classmethod
    def create(cls, user_id: int):
        initial_event = OrderCreated(user_id)
        instance = cls([initial_event])
        instance.changes = [initial_event]
        return instance
