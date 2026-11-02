import logging
import os

from EMHModule.functions import (
    getListOfSubs,
    hasEmhCommented,
    hasEmhCommentedOnPost,
    hasSubOptedOut,
    replaceMoreWithRetry,
    startConversation,
)
from EMHModule.mongodb import updatePostsCommentedOn

logger = logging.getLogger(__name__)


def main():
    subreddits = getListOfSubs()
    if subreddits is None:
        logger.info("No subreddits configured, nothing to do.")
        return

    for post in subreddits.hot(limit=50):
        if hasSubOptedOut(post.subreddit.display_name) or hasEmhCommentedOnPost(post.id):
            continue

        logger.info("--------------------------")
        logger.info(f"Subreddit: {post.subreddit.display_name}")
        logger.info(f"Title: {post.title}")
        logger.info(f"Id: {post.id}")

        if not replaceMoreWithRetry(post.comments) or len(post.comments) == 0:
            continue

        if hasEmhCommented(post.comments):
            # Record it so later runs can skip this post without loading its comments.
            updatePostsCommentedOn(post.id)
            continue

        startConversation(post.comments)


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOGLEVEL", "INFO"))
    main()
