import pytest

import EMHModule.functions as functions


@pytest.fixture(autouse=True)
def fakeState(mocker):
    """Stand in for Reddit and MongoDB so tests never touch the network."""
    mocker.patch.object(functions, '_subs', ['startrek'])
    mocker.patch.object(functions, '_optedOutUsers', set())
    mocker.patch.object(functions, 'insertIntoOptOutTable')
    mocker.patch.object(functions, 'optOutSubReddit')
    mocker.patch.object(functions, 'updatePostsCommentedOn')
    mocker.patch.object(functions, 'updateEmhComments')
