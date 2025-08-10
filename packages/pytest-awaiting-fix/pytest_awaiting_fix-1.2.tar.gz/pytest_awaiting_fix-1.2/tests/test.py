import pytest


@pytest.mark.awaiting_fix('TEST1')
def test_new_comment():
    assert True


@pytest.mark.awaiting_fix('TEST1')
def test_comment_exists():
    assert False

@pytest.mark.awaiting_fix('TEST2')
def test_howdy():
    assert False