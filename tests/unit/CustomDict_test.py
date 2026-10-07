import pytest

from simulator.data_structures.custom_dict import CustomDict
from simulator.message import Message


def create_helper_dict():
    """
    Helper function that creates a dict with 3 messages.
    """
    cd = CustomDict()
    msg1 = Message(source_id=1, dest_id=2, arrival_time=2, content="")
    msg2 = Message(source_id=2, dest_id=3, arrival_time=1, content="")
    msg3 = Message(source_id=1, dest_id=3, arrival_time=3, content="")
    cd.push(msg1)
    cd.push(msg2)
    cd.push(msg3)
    return cd, msg1, msg2, msg3


@pytest.mark.test_id("CD-01")
def test_initial_state():
    """
    Verify that a new CustomDict is empty.
    """
    cd = CustomDict()
    assert cd.size() == 0
    assert cd.empty()


@pytest.mark.test_id("CD-02")
def test_push_increases_size():
    """
    Verify that pushing messages into the dictionary works.
    """
    cd, _, _, _ = create_helper_dict()
    assert cd.size() == 3
    assert not cd.empty()


@pytest.mark.test_id("CD-03")
def test_contains():
    """
    Verify that contains(msg) works properly whether the message is in the dictionary or not.
    """
    cd, _, msg2, _ = create_helper_dict()
    msg_not = Message(source_id=1, dest_id=3, arrival_time=1, content="")
    assert cd.contains(msg2)
    assert not cd.contains(msg_not)


@pytest.mark.test_id("CD-04")
def test_remove():
    """
    Verify that removing a message from the dictionary really removes it.
    """
    cd, msg1, _, _ = create_helper_dict()
    cd.remove(msg1)
    assert not cd.contains(msg1)
    assert cd.size() == 2


@pytest.mark.test_id("CD-05")
def test_remove_non_existent():
    """
    Verifies that removing a message not in the dictionary doesn't affect it.
    """
    cd, _, _, _ = create_helper_dict()
    msg_not = Message(source_id=9, dest_id=9, arrival_time=9, content="")
    cd.remove(msg_not)
    assert cd.size() == 3


@pytest.mark.test_id("CD-06")
def test_get_messages_for_specific_dest():
    """
    Verify that getting messages for a specific destination returns all of them.
    """
    cd, _, msg2, _ = create_helper_dict()
    msg4 = Message(source_id=2, dest_id=3, arrival_time=1, content="")
    cd.push(msg4)
    msgs = cd.get_messages_for_specific_dest(3, 1)
    assert len(msgs) == 2
    assert msg2 in msgs
    assert msg4 in msgs


@pytest.mark.test_id("CD-07")
def test_get_messages_for_dest_empty_result():
    """
    Verify that getting messages for a non-existent destination returns an empty list.
    """
    cd, _, _, _ = create_helper_dict()
    msgs = cd.get_messages_for_specific_dest(dest_id=99, current_round=99)
    assert msgs == []


@pytest.mark.test_id("CD-08")
def test_get_all_messages():
    """
    Verify that getting all the messages returns all of them.
    """
    cd, msg1, msg2, msg3 = create_helper_dict()
    all_msgs = cd.get_all_messages()
    assert len(all_msgs) == 3
    assert set(all_msgs) == {msg1, msg2, msg3}


@pytest.mark.test_id("CD-09")
def test_clear_key():
    """
    Verify that clearing a specific (dest, round) key removes only its messages.
    """
    cd, msg1, msg2, msg3 = create_helper_dict()
    msg4 = Message(source_id=2, dest_id=3, arrival_time=1, content="")
    cd.push(msg4)
    cd.clear_key(dest_id=3, round=1)  # Removes msg2 and msg4
    assert cd.size() == 2
    assert not cd.contains(msg2)
    assert not cd.contains(msg4)
    assert cd.contains(msg1)
    assert cd.contains(msg3)


@pytest.mark.test_id("CD-10")
def test_clear():
    """
    Verify that clearing the dictionary empties it.
    """
    cd, _, _, _ = create_helper_dict()
    cd.clear()
    assert cd.empty()
    assert cd.size() == 0
