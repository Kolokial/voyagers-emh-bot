import pytest
from unittest.mock import MagicMock
from src.functions import isEmh  # Assuming your function is in functions.py
from tests.mocks.Redditor import Redditor


def test_isEmh():
    # Test when redditor is None
    result = isEmh(None)
    assert result == False, "Expected False when redditor is None"

    # Test when redditor's name matches the predefined username
    redditor = Redditor(name="VoyagersEMH")
    result = isEmh(redditor)
    assert result == True, "Expected True when redditor's name matches the username"

    # Test when redditor's name does not match the predefined username
    redditor = Redditor(name="other_user")
    result = isEmh(redditor)
    assert result == False, "Expected False when redditor's name does not match the username"
