import EMHModule.functions as functions
from EMHModule.functions import (
    doesEmhReplyExist,
    hasEmhCommented,
    hasMoreQuotesCriteria,
    hasSubOptedOut,
    hasUserOptedOut,
    isModOptingSubOut,
    isUserOptingOut,
    postIdFromComment,
    redditUserName,
    startConversation,
)
from tests.mocks.comments import makeComment
from tests.mocks.Redditor import Redditor

EMH = redditUserName


# doesEmhReplyExist / hasEmhCommented

def test_doesEmhReplyExist_returns_false_not_none():
    comment = makeComment(replies=[makeComment(author="a"), makeComment(author="b")])
    assert doesEmhReplyExist(comment) is False


def test_doesEmhReplyExist_true():
    comment = makeComment(replies=[makeComment(author="a"), makeComment(author=EMH)])
    assert doesEmhReplyExist(comment) is True


def test_hasEmhCommented_checks_every_thread():
    forest = [
        makeComment(author="a"),
        makeComment(author="b", replies=[makeComment(author="c", replies=[makeComment(author=EMH)])]),
    ]
    assert hasEmhCommented(forest) is True
    assert hasEmhCommented([makeComment(author="a"), makeComment(author="b")]) is False


# hasMoreQuotesCriteria

def test_more_quotes_reply_to_emh_without_answer():
    comment = makeComment("More quotes please!", parent=makeComment(author=EMH))
    assert hasMoreQuotesCriteria(comment) is True


def test_more_quotes_already_answered():
    comment = makeComment("more quotes", parent=makeComment(author=EMH),
                          replies=[makeComment(author=EMH)])
    assert hasMoreQuotesCriteria(comment) is False


def test_more_quotes_parent_not_emh():
    comment = makeComment("more quotes", parent=makeComment(author="someone_else"))
    assert hasMoreQuotesCriteria(comment) is False


def test_more_quotes_no_request():
    comment = makeComment("nice one", parent=makeComment(author=EMH))
    assert hasMoreQuotesCriteria(comment) is False


def test_more_quotes_from_emh_itself():
    comment = makeComment("Ask me for more quotes", author=EMH, parent=makeComment(author=EMH))
    assert hasMoreQuotesCriteria(comment) is False


# Opt-outs

def test_hasUserOptedOut_checks_whole_list(mocker):
    mocker.patch.object(functions, '_optedOutUsers', {'first', 'second', 'third'})
    assert hasUserOptedOut('third') is True
    assert hasUserOptedOut('Third') is True
    assert hasUserOptedOut('fourth') is False


def test_isUserOptingOut_needs_the_command_on_its_own():
    user = Redditor("someone")
    assert isUserOptingOut("optout", user) is True
    assert isUserOptingOut("OptOut!", user) is True
    assert isUserOptingOut("  ignore me ", user) is True
    assert isUserOptingOut("you can opt out of that", user) is False
    assert isUserOptingOut("optout", Redditor(EMH)) is False


def test_mod_opting_sub_out_with_capitalised_name(mocker):
    author = mocker.MagicMock()
    author.name = "a_mod"
    author.moderated.return_value = ["StarTrek"]
    comment = makeComment("GTFO VoyagersEMH", subreddit="StarTrek")
    comment.author = author

    assert isModOptingSubOut(comment) is True
    functions.optOutSubReddit.assert_called_once_with("StarTrek")
    assert hasSubOptedOut("StarTrek") is True


def test_non_mod_cannot_opt_sub_out(mocker):
    author = mocker.MagicMock()
    author.name = "not_a_mod"
    author.moderated.return_value = []
    comment = makeComment("gtfo voyagersemh")
    comment.author = author

    assert isModOptingSubOut(comment) is False
    assert hasSubOptedOut("StarTrek") is False


# startConversation

def test_postIdFromComment_strips_prefix():
    assert postIdFromComment(makeComment(link_id="t3_abc123")) == "abc123"


def test_replies_to_mention_that_has_other_replies(mocker):
    reply = mocker.patch.object(functions, 'replyWithEMHQuote')
    mention = makeComment("I love the Doctor", replies=[makeComment("me too", author="b")])
    assert startConversation([mention]) is True
    reply.assert_called_once_with(mention)


def test_finds_mention_nested_under_normal_comment(mocker):
    reply = mocker.patch.object(functions, 'replyWithEMHQuote')
    mention = makeComment("Voyager's EMH is the best", author="b")
    assert startConversation([makeComment("great episode", replies=[mention])]) is True
    reply.assert_called_once_with(mention)


def test_replies_only_once_per_post(mocker):
    reply = mocker.patch.object(functions, 'replyWithEMHQuote')
    forest = [
        makeComment("hi", replies=[makeComment("the doctor!", author="b")]),
        makeComment("the emh!", author="c"),
    ]
    startConversation(forest)
    assert reply.call_count == 1


def test_skips_deleted_and_opted_out_authors(mocker):
    reply = mocker.patch.object(functions, 'replyWithEMHQuote')
    mocker.patch.object(functions, '_optedOutUsers', {'quiet'})
    forest = [makeComment("the doctor", author=None), makeComment("the doctor", author="quiet")]
    assert startConversation(forest) is False
    reply.assert_not_called()


def test_opt_out_comment_is_recorded(mocker):
    reply = mocker.patch.object(functions, 'replyWithEMHQuote')
    startConversation([makeComment("optout", author="someone")])
    functions.insertIntoOptOutTable.assert_called_once_with("someone")
    assert hasUserOptedOut("someone") is True
    reply.assert_not_called()


def test_replyWithEMHQuote_records_bare_post_id():
    comment = makeComment("the doctor", link_id="t3_abc123")
    comment.reply.return_value.id = "newcomment"
    functions.replyWithEMHQuote(comment)
    functions.updatePostsCommentedOn.assert_called_once_with("abc123")
    functions.updateEmhComments.assert_called_once_with("newcomment")
