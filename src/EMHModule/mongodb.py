import logging
import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo.database import Database
from pymongo.errors import ConfigurationError
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

logger = logging.getLogger(__name__)

# Case-insensitive matching, used for subreddit names.
CASE_INSENSITIVE = {"locale": "en", "strength": 2}


@lru_cache(maxsize=None)
def getDatabase() -> Database:
    """Connect on first use, so importing this module has no side effects."""
    uri = os.getenv('MONGODB_CONNECTION_STRING')
    if not uri:
        raise RuntimeError("MONGODB_CONNECTION_STRING is not set")

    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
    except ConfigurationError:
        logger.error("Invalid MongoDB URI. Is the host name in your connection string correct?")
        raise

    return client.voyagersEMHBot


def _table(name: str):
    return getDatabase()[name]


def _insertIfMissing(tableName: str, document: dict):
    # Upsert so repeated runs don't create duplicate records.
    result = _table(tableName).update_one(document, {"$setOnInsert": document}, upsert=True)
    if result.upserted_id is not None:
        logger.info(f"Added {document} to {tableName}")


def insertIntoOptOutTable(username: str):
    _insertIfMissing('user_optout', {"name": username})


def getOptOutList() -> list[str]:
    return [doc['name'] for doc in _table('user_optout').find()]


def optOutSubReddit(subredditName: str):
    result = _table('subreddits').delete_many({"name": subredditName}, collation=CASE_INSENSITIVE)
    logger.info(f"Removed {result.deleted_count} subreddit record(s) for {subredditName}")


def getSubreddits() -> list[str]:
    subs = [doc['name'].lower() for doc in _table('subreddits').find()]
    if not subs:
        logger.info("No subreddits found.")
    return subs


def updatePostsCommentedOn(post_id: str):
    _insertIfMissing('commented_posts', {"post_id": post_id})


def hasEmhCommentedOnPost(post_id: str) -> bool:
    # Older records were saved with Reddit's "t3_" prefix, so check both forms.
    query = {"post_id": {"$in": [post_id, f"t3_{post_id}"]}}
    return _table('commented_posts').find_one(query) is not None


def updateEmhComments(comment_id: str):
    _insertIfMissing('emh_comments', {"comment_id": comment_id})


def getEmhComments() -> list[str]:
    return [doc['comment_id'] for doc in _table('emh_comments').find()]
