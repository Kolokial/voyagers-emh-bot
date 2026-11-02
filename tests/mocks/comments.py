from types import SimpleNamespace
from unittest.mock import MagicMock

from tests.mocks.Redditor import Redditor


def makeComment(body: str = "", author: str | None = "someone", replies=None,
                subreddit: str = "StarTrek", parent=None, link_id: str = "t3_post1"):
    comment = MagicMock()
    comment.body = body
    comment.author = Redditor(author) if author is not None else None
    comment.replies = replies or []
    comment.subreddit = SimpleNamespace(display_name=subreddit)
    comment.link_id = link_id
    comment.parent.return_value = parent
    return comment
