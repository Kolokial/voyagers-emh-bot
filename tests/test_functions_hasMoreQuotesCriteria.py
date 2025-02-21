
import pytest
from unittest.mock import MagicMock
# Assuming these are the actual imports
from src.functions import hasMoreQuotesCriteria, isEmh, doesEmhReplyExist, moreQuotesRegex

# Mocking isEmh and doesEmhReplyExist for the tests


@pytest.fixture(autouse=True)
def mock_dependencies():
    # Mock the isEmh function
    global isEmh
    isEmh = MagicMock()

    # Mock the doesEmhReplyExist function
    global doesEmhReplyExist
    doesEmhReplyExist = MagicMock()

# Test case for hasMoreQuotesCriteria


def test_hasMoreQuotesCriteria():
    # Mocking a Comment object
    comment = MagicMock()
    parent_comment = MagicMock()

    # Setting the body and parent of the comment
    comment.body = "This is a test comment with a quote"
    parent_comment.body = "This is the parent comment"

    # Mock the parent method to return the parent comment
    comment.parent.return_value = parent_comment

    # Mock the results for isEmh and doesEmhReplyExist
    isEmh.return_value = False  # Simulate that comment.author is not "EMH"
    doesEmhReplyExist.return_value = False  # Simulate no reply existing

    # Mock regex search (simulate a match)
    moreQuotesRegex = MagicMock()
    moreQuotesRegex.search.return_value = True  # Simulate a successful regex match

    # Run the test when all conditions are true
    result = hasMoreQuotesCriteria(comment)
    assert result == True, "Expected True when all conditions are met"

    # Now test with a failure in one of the conditions

    # Test when the regex doesn't match
    moreQuotesRegex.search.return_value = False
    result = hasMoreQuotesCriteria(comment)
    assert result == False, "Expected False when regex doesn't match"

    # Test when isEmh(comment.author) returns True
    isEmh.return_value = True
    result = hasMoreQuotesCriteria(comment)
    assert result == False, "Expected False when comment.author is 'EMH'"

    # Test when isEmh(parent.author) returns False
    isEmh.return_value = False
    parent_comment.author = MagicMock(
        name="parent_author")  # Mock parent.author
    result = hasMoreQuotesCriteria(comment)
    assert result == False, "Expected False when parent.author is not 'EMH'"

    # Test when doesEmhReplyExist(comment) returns True (meaning a reply exists)
    doesEmhReplyExist.return_value = True
    result = hasMoreQuotesCriteria(comment)
    assert result == False, "Expected False when a reply exists"
