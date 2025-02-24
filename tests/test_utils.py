import os

import pytest

from lyrics_extractor.util import with_stdout_redirect


def func():
    print("...")


@pytest.fixture
def setup_and_teardown():
    yield
    os.remove(f"{func.__name__}.txt")


def test_with_stdout_redirect(setup_and_teardown):
    with_stdout_redirect(func)
    with open(f"{func.__name__}.txt", "r") as f:
        assert "...\n" == f.read()
