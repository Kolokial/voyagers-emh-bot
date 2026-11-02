import logging
import os
from datetime import datetime, timezone

from praw.exceptions import PRAWException
from prawcore.exceptions import PrawcoreException

from EMHModule.functions import getRedditInstance, hasSubOptedOut, replaceMoreWithRetry
from EMHModule.lookForMoreQuotes import lookForMoreQuotesRequest
from EMHModule.mongodb import getEmhComments

logger = logging.getLogger(__name__)

MAX_COMMENT_AGE_DAYS = 30


def main():
    reddit = getRedditInstance()

    for commentId in getEmhComments():
        comment = reddit.comment(commentId)
        try:
            written = datetime.fromtimestamp(comment.created_utc, timezone.utc)
            age = datetime.now(timezone.utc) - written
            if comment.locked or age.days > MAX_COMMENT_AGE_DAYS:
                continue
            if hasSubOptedOut(comment.subreddit.display_name):
                continue
            comment.refresh()
        except (PrawcoreException, PRAWException) as e:
            # Deleted or removed comments can't be loaded; skip them.
            logger.warning(f"Could not load comment {commentId}: {e}")
            continue

        if replaceMoreWithRetry(comment.replies):
            lookForMoreQuotesRequest(comment.replies)


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOGLEVEL", "INFO"))
    main()
