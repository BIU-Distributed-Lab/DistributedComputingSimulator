import pytest

from simulator.data_structures.custom_min_heap import CustomMinHeap
from simulator.message import Message


def create_helper_heap():
    """
    Helper function that creates a heap with 3 messages.
    """
    cmh = CustomMinHeap()
    msg1 = Message(source_id=1, dest_id=2, arrival_time=2, content="")
    msg2 = Message(source_id=2, dest_id=3, arrival_time=1, content="")
    msg3 = Message(source_id=1, dest_id=3, arrival_time=3, content="")
    cmh.push(msg1)
    cmh.push(msg2)
    cmh.push(msg3)
    return cmh, msg1, msg2, msg3


def test_initial_state():
    """
    CMH-01
    Verify that a new CustomMinHeap is empty.
    """
    cmh = CustomMinHeap()
    assert cmh.size() == 0
    assert cmh.empty() is True
    assert cmh.total_messages_sent == 0
    assert cmh.total_messages_received == 0


def test_push_increases_size():
    """
    CMH-02
    Verify that pushing messages into the heap works.
    """
    cmh, _, _, _ = create_helper_heap()
    assert cmh.size() == 3
    assert cmh.empty() is False
    assert cmh.total_messages_sent == 3


def test_pop_ordering_by_arrival_time():
    """
    CMH-03
    Verify that poping messages return them in the correct order.
    """
    cmh, msg1, msg2, _ = create_helper_heap()
    first_popped = cmh.pop()  # msg2 has arrival_time = 1
    assert first_popped == msg2
    assert cmh.size() == 2

    second_popped = cmh.pop()  # msg1 has arrival_time = 2
    assert second_popped == msg1
    assert cmh.size() == 1


def test_pop_until_empty():
    """
    CMH-04
    Verify that empty() works correctly.
    """
    cmh, _, _, msg3 = create_helper_heap()
    cmh.pop()  # pops msg2
    cmh.pop()  # pops msg1
    assert cmh.empty() is False

    last_popped = cmh.pop()
    assert last_popped == msg3
    assert cmh.empty() is True
    assert cmh.size() == 0
    assert cmh.total_messages_received == 3


def test_pop_empty_heap_raises_error():
    """
    CMH-05
    Verify that poping an empty heap raises an error.
    """
    cmh = CustomMinHeap()
    with pytest.raises(IndexError):
        cmh.pop()


def test_tie_breaking_order():
    """
    CMH-06
    Verify that if 2 messages have the same arrival time,
    the one that will pop first is the one that was pushed first.
    """
    cmh = CustomMinHeap()
    msg_a = Message(source_id=1, dest_id=2, arrival_time=5, content="")
    msg_b = Message(source_id=3, dest_id=4, arrival_time=5, content="")
    cmh.push(msg_a)
    cmh.push(msg_b)
    assert cmh.pop() == msg_a
    assert cmh.pop() == msg_b

