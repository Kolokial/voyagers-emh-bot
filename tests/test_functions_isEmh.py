from EMHModule.functions import isEmh
from tests.mocks.Redditor import Redditor


def test_isEmh_none():
    assert isEmh(None) is False


def test_isEmh_matches_case_insensitively():
    assert isEmh(Redditor("VoyagersEMH")) is True
    assert isEmh(Redditor("voyagersemh")) is True


def test_isEmh_other_user():
    assert isEmh(Redditor("other_user")) is False
