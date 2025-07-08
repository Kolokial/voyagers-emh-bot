from random import randrange
from EMHModule.mongodb import *
from praw.models import Submission, Comment, Subreddit, comment_forest, Redditor
from praw import Reddit
import praw
import re
import json
import os
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

def getRedditInstance() -> Reddit:
    return reddit


# subs = [
#     "kolotesting"
# ]

# startreksub = reddit.subreddit("+".join(subs))
subs = getSubreddits()
if subs.__len__() == 0:
    exit()

startreksub = reddit.subreddit("+".join(subs))


def isEmh(redditor: Redditor):
    if redditor == None:
        return False

    if redditor.name == redditUserName:
        return True
    else:
        return False


def hasMoreQuotesCriteria(comment: Comment):
    parent = comment.parent()
    print(moreQuotesRegex.search(comment.body.lower()))

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
    updateEmhComments(doctorsComment.link_id)
    print("Replied to:" + comment.body)
    print("Replied with: "+reply)


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


def hasSubOptedOut(comment: Comment) -> bool:
    subreddit = comment.subreddit.display_name
    return subreddit.lower() not in subs
