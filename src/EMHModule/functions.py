import json
import logging
import os
import re
from random import choice
from time import sleep

import praw
from dotenv import load_dotenv
from praw.models import Comment, Redditor, Subreddit
from prawcore.exceptions import PrawcoreException

from EMHModule.mongodb import (
    getOptOutList,
    getSubreddits,
    hasEmhCommentedOnPost as dbHasEmhCommentedOnPost,
    insertIntoOptOutTable,
    optOutSubReddit,
    updateEmhComments,
    updatePostsCommentedOn,
)

load_dotenv()

logger = logging.getLogger(__name__)

redditUserName = "VoyagersEMH"

doctorRegex = re.compile(r"\b(voyager'?s ?emh|the doctor|the emh)\b", re.IGNORECASE)
moreQuotesRegex = re.compile(r"\bmore quotes\b", re.IGNORECASE)
# The whole comment has to be the command, so ordinary sentences such as
# "you can opt out of that" don't opt people out by accident.
optOutRegex = re.compile(r"^\W*(ignore ?me|opt ?out)\W*$", re.IGNORECASE)
subOptOutRegex = re.compile(r"\bgtfo voyagersemh\b", re.IGNORECASE)

_quotesPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'emh-quotes.json')
with open(_quotesPath, encoding='utf-8') as quotesFile:
    emhQuotes = json.load(quotesFile)

_reddit = None
_subs = None
_optedOutUsers = None


def getRedditInstance() -> praw.Reddit:
    global _reddit
    if _reddit is None:
        _reddit = praw.Reddit(
            user_agent="LCARS:Voyagers EMH:0.1 (by u/koloqial)",
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            username=redditUserName,
            password=os.getenv('REDDIT_PASSWORD')
        )
    return _reddit


def getSubs() -> list[str]:
    """Lowercase names of the subreddits the bot is active in."""
    global _subs
    if _subs is None:
        _subs = getSubreddits()
    return _subs


def getListOfSubs() -> Subreddit | None:
    subs = getSubs()
    if not subs:
        return None
    return getRedditInstance().subreddit("+".join(subs))


def replaceMoreWithRetry(forest, attempts: int = 3, delay: int = 5) -> bool:
    """Load the hidden "more comments" in a comment forest, retrying on Reddit errors."""
    for attempt in range(1, attempts + 1):
        try:
            forest.replace_more()
            return True
        except PrawcoreException as e:
            logger.warning(f"replace_more failed (attempt {attempt}/{attempts}): {e}")
            sleep(delay)
    return False


def isEmh(redditor: Redditor | None) -> bool:
    return redditor is not None and redditor.name.lower() == redditUserName.lower()


def doesEmhReplyExist(comment: Comment) -> bool:
    return any(isEmh(reply.author) for reply in comment.replies)


def hasEmhCommented(commentForest) -> bool:
    for comment in commentForest:
        if isEmh(comment.author) or hasEmhCommented(comment.replies):
            return True
    return False


def hasMoreQuotesCriteria(comment: Comment) -> bool:
    """True when someone replied "more quotes" to the EMH and hasn't had an answer yet."""
    if isEmh(comment.author) or not moreQuotesRegex.search(comment.body):
        return False
    if doesEmhReplyExist(comment):
        return False
    # Checked last because parent() can cost an API call.
    return isEmh(comment.parent().author)


def postIdFromComment(comment: Comment) -> str:
    # link_id is the post's full name, e.g. "t3_abc123".
    return comment.link_id.split('_', 1)[-1]


def buildReply(quote: dict) -> str:
    horizontalRule = "\n\n---\n\n"
    askForMore = "^(Ask me for more quotes or you can summon me!)"
    contact = "\n\n^(Is this annoying? Can I do better? Tell my [creator](https://www.reddit.com/user/koloqial)!)"
    optout = "\n\n ^(If you wish for the EMH to not reply to you ever again, simply reply with 'optout')"
    subOptOut = "\n\n ^(If you're a mod and want this bot to leave the sub, please reply with 'gtfo voyagersemh')"
    return ("> " + quote['quote'] + "\n\n[" + quote['episodeName'] + "](" + quote['url'] + ")\n"
            + horizontalRule + askForMore + contact + optout + subOptOut)


def replyWithEMHQuote(comment: Comment):
    if isEmh(comment.author):
        return

    reply = buildReply(choice(emhQuotes))
    doctorsComment = comment.reply(body=reply)
    updatePostsCommentedOn(postIdFromComment(comment))
    updateEmhComments(doctorsComment.id)
    logger.info(f"Replied to: {comment.body}")
    logger.info(f"Replied with: {reply}")


def isUserOptingOut(body: str, redditor: Redditor | None) -> bool:
    if isEmh(redditor):
        return False
    return optOutRegex.search(body) is not None


def _getOptedOutUsers() -> set[str]:
    global _optedOutUsers
    if _optedOutUsers is None:
        _optedOutUsers = {name.lower() for name in getOptOutList()}
    return _optedOutUsers


def hasUserOptedOut(username: str) -> bool:
    return username.lower() in _getOptedOutUsers()


def optUserOut(username: str):
    insertIntoOptOutTable(username)
    _getOptedOutUsers().add(username.lower())


def isUserMod(redditor: Redditor | None, subredditName: str) -> bool:
    if redditor is None:
        return False
    # praw compares Subreddit objects to strings case-insensitively.
    return any(sub == subredditName for sub in redditor.moderated())


def hasSubOptOutCriteria(body: str) -> bool:
    return subOptOutRegex.search(body) is not None


def isModOptingSubOut(comment: Comment) -> bool:
    if isEmh(comment.author) or not hasSubOptOutCriteria(comment.body):
        return False

    subreddit = comment.subreddit.display_name
    if not isUserMod(comment.author, subreddit):
        return False

    optOutSubReddit(subreddit)
    subs = getSubs()
    if subreddit.lower() in subs:
        subs.remove(subreddit.lower())
    return True


def hasSubOptedOut(subredditName: str) -> bool:
    return subredditName.lower() not in getSubs()


def hasEmhCommentedOnPost(post_id: str) -> bool:
    return dbHasEmhCommentedOnPost(post_id)


def shouldSkipComment(comment: Comment) -> bool:
    """Handle opt-out commands and return True if the EMH must not reply to this comment."""
    author = comment.author
    if author is None or isEmh(author):
        return True

    subreddit = comment.subreddit.display_name
    if hasSubOptedOut(subreddit):
        logger.info(f"{subreddit} has opted out")
        return True
    if isModOptingSubOut(comment):
        logger.info(f"{author.name} is opting {subreddit} out")
        return True
    if hasUserOptedOut(author.name):
        logger.info(f"{author.name} has opted out")
        return True
    if isUserOptingOut(comment.body, author):
        logger.info(f"{author.name} is opting out")
        optUserOut(author.name)
        return True
    return False


def startConversation(comments) -> bool:
    """Reply to the first comment mentioning the doctor. Returns True once a reply is made."""
    for comment in comments:
        if not shouldSkipComment(comment) \
                and doctorRegex.search(comment.body) \
                and not doesEmhReplyExist(comment):
            logger.info("Found a comment mentioning the doctor")
            logger.info(f"Comment written by: {comment.author}")
            logger.info(f"Comment: {comment.body}")
            logger.info(f"Permalink: https://reddit.com{comment.permalink}")
            replyWithEMHQuote(comment)
            return True

        if hasSubOptedOut(comment.subreddit.display_name):
            return False

        if startConversation(comment.replies):
            return True
    return False
