from es import Order
from events import OrderCreated, StatusChanged


def test_should_create_order():
    order = Order.create(user_id=1)
    assert order.changes == [OrderCreated(user_id=1)]


def test_should_emit_set_status_event():
    order = Order([OrderCreated(user_id=1)])
    order.status = "confirmed"
    assert order.changes == [StatusChanged(new_status="confirmed")]
