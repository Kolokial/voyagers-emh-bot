import EMHModule.lookForMoreQuotes as lookForMoreQuotes
from EMHModule.functions import redditUserName
from tests.mocks.comments import makeComment


def test_answers_more_quotes_request_without_crashing(mocker):
    reply = mocker.patch.object(lookForMoreQuotes, 'replyWithEMHQuote')
    request = makeComment("more quotes", parent=makeComment(author=redditUserName))
    lookForMoreQuotes.lookForMoreQuotesRequest([request])
    reply.assert_called_once_with(request)


def test_ignores_other_replies(mocker):
    reply = mocker.patch.object(lookForMoreQuotes, 'replyWithEMHQuote')
    lookForMoreQuotes.lookForMoreQuotesRequest(
        [makeComment("thanks!", parent=makeComment(author=redditUserName))])
    reply.assert_not_called()
