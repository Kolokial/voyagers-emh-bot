
import pytest
# Assuming these are the actual imports
from src.functions import hasMoreQuotesCriteria, redditUserName


def test_hasMoreQuotesCriteria(mocker):

    mock_isEmh = mocker.patch('src.functions.isEmh')
    mock_doesEmhReplyExist = mocker.patch('src.functions.doesEmhReplyExist')

    mock_isEmh.return_value = False
    mock_doesEmhReplyExist.return_value = True

    # Mocking a Comment object
    comment = mocker.MagicMock()
    parent_comment = mocker.MagicMock()
    parent_comment.author.name = redditUserName

    # Setting the body and parent of the comment
    comment.body = "This is a test comment asking for more quotes"
    parent_comment.body = "This is the parent comment"

    # Mock the parent method to return the parent comment
    comment.parent.return_value = parent_comment

    # Mock regex search (simulate a match)
    # moreQuotesRegex = MagicMock()
    # moreQuotesRegex.search.return_value = True  # Simulate a successful regex match

    # Run the test when all conditions are true
    result = hasMoreQuotesCriteria(comment)
    assert result == True, "Expected True when all conditions are met"

    # # Now test with a failure in one of the conditions

    # # Test when the regex doesn't match
    # comment.body = "Comment not asking for quotes"
    # # moreQuotesRegex.search.return_value = False
    # doesEmhReplyExist.return_value = True  # Simulate no reply existing
    # result = hasMoreQuotesCriteria(comment)
    # assert result == False, "Expected False when regex doesn't match"

    # # Test when isEmh(comment.author) returns True
    # isEmh.return_value = True
    # result = hasMoreQuotesCriteria(comment)
    # assert result == False, "Expected False when comment.author is 'EMH'"

    # # Test when isEmh(parent.author) returns False
    # isEmh.return_value = False
    # parent_comment.author = MagicMock(
    #     name="parent_author")  # Mock parent.author
    # result = hasMoreQuotesCriteria(comment)
    # assert result == False, "Expected False when parent.author is not 'EMH'"

    # # Test when doesEmhReplyExist(comment) returns True (meaning a reply exists)
    # doesEmhReplyExist.return_value = True
    # result = hasMoreQuotesCriteria(comment)
    # assert result == False, "Expected False when a reply exists"
