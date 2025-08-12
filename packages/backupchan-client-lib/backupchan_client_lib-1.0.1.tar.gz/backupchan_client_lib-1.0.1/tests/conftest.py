import pytest
from backupchan import Connection

TEST_TOKEN = "test-token"

@pytest.fixture
def conn():
    return Connection("http://localhost", 5000, TEST_TOKEN)
