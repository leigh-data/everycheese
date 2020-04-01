import pytest
from .factories import CheeseFactory


@pytest.fixture
def cheese():
    return CheeseFactory()
