from typing import List
from functools import singledispatchmethod
from events import Event, OrderCreated, StatusChanged


class Order:
    def __init__(self, events: List[Event]):
        self.changes: List[Event] = []
        for event in events:
            self.apply(event)

    @singledispatchmethod
    def apply(self, event):
        raise ValueError("Unknown event!")

    @apply.register
    def apply_order_created(self, event: OrderCreated):
        self.user_id = event.user_id
        self._status = "new"

    @apply.register
    def apply_status_changed(self, event: StatusChanged):
        self._status = event.new_status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status: str):
        if new_status not in {"new", "paid", "confirmed", "shipped"}:
            raise ValueError(f"{new_status} is not a valid status")
        event = StatusChanged(new_status)
        self.apply(event)
        self.changes.append(event)

    @classmethod
    def create(cls, user_id: int):
        initial_event = OrderCreated(user_id)
        instance = cls([initial_event])
        instance.changes.append(initial_event)
        return instance
