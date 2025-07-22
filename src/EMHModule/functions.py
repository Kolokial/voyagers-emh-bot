from random import randrange
from EMHModule.mongodb import updatePostsCommentedOn, updateEmhComments, getOptOutList, insertIntoOptOutTable, getSubreddits, optOutSubReddit, hasEmhCommentedOnPost as dbHasEmhCommentedOnPost

from praw.models import Submission, Comment, Subreddit, comment_forest, Redditor
from praw import Reddit
from types import NoneType
import time
import praw
import re
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

redditUserName = "VoyagersEMH"
doctorRegex = re.compile(r'voyager\'?s ?emh|the doctor|the emh')
moreQuotesRegex = re.compile(r'more quotes')
optOutRegex = re.compile(r'ignore ?me|opt ?out')
subOptOutRegex = re.compile(r'gtfo voyagersemh')
file = open(os.path.dirname(os.path.abspath(__file__)) +
            '/../../data/emh-quotes.json')
emhQuotes = json.load(file)


reddit = praw.Reddit(
    user_agent="LCARS:Voyagers EMH:0.1 (by u/koloqial)",
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    username=redditUserName,
    password=os.getenv('REDDIT_PASSWORD')
)

logging.basicConfig(level=os.getenv("LOGLEVEL", "INFO"))
def getRedditInstance() -> Reddit:
    return reddit



subs = getSubreddits()
if subs.__len__() == 0:
    exit()


def getListOfSubs() -> str: 
    return reddit.subreddit("+".join(subs))

    # return reddit.subreddit("+".join([
    #     "kolotesting"
    # ]))

def isEmh(redditor: Redditor):
    if redditor == None:
        return False

    if redditor.name == redditUserName:
        return True
    else:
        return False


def hasMoreQuotesCriteria(comment: Comment):
    parent = comment.parent()
    logging.info(moreQuotesRegex.search(comment.body.lower()))

    if moreQuotesRegex.search(comment.body.lower()) \
            and not isEmh(comment.author) \
            and isEmh(parent.author) \
            and doesEmhReplyExist(comment):
        return True
    return False


def hasEmhCommented(commentForest: comment_forest):
    for comment in commentForest:
        if (isEmh(comment.author)):
            return True
        if (comment.replies.__len__() != 0):
            comment.replies.replace_more(None, 0)
            return hasEmhCommented(comment.replies)
        else:
            return False


def doesEmhReplyExist(comment: Comment):
    if comment.replies.__len__() == 0:
        return False
    else:
        for reply in comment.replies:
            if (isEmh(reply.author)):
                return True


def getEmhReply(comment: Comment):
    if comment.replies.__len__() == 0:
        return

    if isEmh(comment.author):
        return comment

    for reply in comment.replies:
        if isEmh(reply.author):
            return reply


def replyWithEMHQuote(comment: Comment):
    if (isEmh(comment.author)):
        return

    index = randrange(emhQuotes.__len__())
    quote = "> "+emhQuotes[index]['quote']
    episode = emhQuotes[index]['episodeName']
    url = emhQuotes[index]['url']
    horizontalRule = "\n\n---\n\n"
    askForMore = "^(Ask me for more quotes or you can summon me!)"
    contact = "\n\n^(Is this annoying? Can I do better? Tell my [creator](https://www.reddit.com/user/koloqial)!)"
    optout = "\n\n ^(If you wish for the EMH to not reply to you ever again, simply reply with 'optout')"
    subOptOut = "\n\n ^(If you're a mod and want this bot to leave the sub, please reply with 'gtfo voyagersemh')"

    addMoreQuotes = "\n You can contribute to the quote list [here]()!\n"
    reply = quote + "\n\n["+episode+"]("+url+")\n"+horizontalRule + \
        askForMore + contact + optout + subOptOut

    doctorsComment = comment.reply(body=reply)
    updatePostsCommentedOn(comment.link_id)
    updateEmhComments(doctorsComment.id)
    logging.info(f"Replied to: {comment.body}")
    logging.info(f"Replied with: {reply}")


def isUserOptingOut(comment: Comment, redditor: Redditor):
    if isEmh(redditor):
        return False
    return optOutRegex.search(comment) != None


def hasUserOptedOut(username: str) -> bool:
    optoutList = getOptOutList()
    for user in optoutList:
        return True if user == username else False


def isUserMod(redditor: Redditor, subredditName: str) -> bool:
    if redditor == None:
        return False
    for sub in redditor.moderated():
        if sub == subredditName:
            return True
    return False


def hasSubOptOutCriteria(comment: Comment) -> bool:
    return subOptOutRegex.search(comment) != None


def isModOptingSubOut(comment: Comment) -> bool:
    author = comment.author
    subreddit = comment.subreddit.display_name
    if hasSubOptOutCriteria(comment.body):
        if isUserMod(author, subreddit):
            optOutSubReddit(subreddit)
            subs.remove(subreddit)
            return True
    else:
        return False


def hasSubOptedOut(subredditName: str) -> bool:
    return subredditName.lower() not in subs

def hasEmhCommentedOnPost(post_id) -> bool:
    return dbHasEmhCommentedOnPost(post_id)

def startConversation(comments: comment_forest):
    comment: Comment
    for comment in comments:
        if isEmh(comment.author) == None:
            continue

        author = comment.author
        if (hasSubOptedOut(comment.subreddit.display_name)):
            logging.info(f"{comment.subreddit.display_name} has opted out")
            continue
        elif (isModOptingSubOut(comment)):
            logging.info(f"{comment.author.name} is opting {comment.subreddit.display_name} out")
            continue
        elif author != None and hasUserOptedOut(author.name):
            logging.info(f"{comment.author.name} has opting out")
            continue
        elif isUserOptingOut(comment.body, author):
            logging.info(f"{comment.author.name} is opting out")
            insertIntoOptOutTable(author)
            continue

        # comment.refresh()
        # comment.replies.replace_more(limit=None, threshold=0)
        # logging.info(f"Comment written by :", author)
        # logging.info(f"replies", comment.replies.__len__())
        # logging.info(f"comment", comment.body)
        # logging.info(f"Id:", comment.id)
        if (doctorRegex.search(comment.body.lower()) is not None):
            logging.info(f"Found a comment mentioning the doctor")
            logging.info(f"---------------------------------\n")
            logging.info(f"Post Title: {comment.submission.title}")
            logging.info(f"Comment written by : {comment.author}")
            logging.info(f"replies {comment.replies.__len__()}")
            logging.info(f"comment {comment.body}")
            logging.info(f"Id: {comment.id}")
            logging.info(f"permalink: https://reddit.com{comment.permalink}")
            if (doesEmhReplyExist(comment) == False):
                logging.info(f"with no previous replies")
                replyWithEMHQuote(comment)
                return

            if (comment.replies.__len__()):
                #time.sleep(2)
                startConversation(comment.replies)
