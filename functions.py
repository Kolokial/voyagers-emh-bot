from random import randrange
from monogodb import *
import praw
import re
import json
import os

redditUserName = "VoyagersEMH"
doctorRegex = re.compile(r'voyager\'?s ?emh|the doctor')
moreQuotesRegex = re.compile(r'more quotes')
optOutRegex = re.compile(r'ignore ?me|opt ?out')
file = open(os.path.dirname(os.path.abspath(__file__))+'/emh-quotes.json')
emhQuotes = json.load(file)


reddit = praw.Reddit(
    user_agent="LCARS:Voyagers EMH:0.1 (by u/koloqial)",
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    username=redditUserName,
    password=os.getenv('REDDIT_PASSWORD')
)

subs = [
    'shittydaystrom',
    'startrek',
    'voyager',
    'startrekmemes',
    'voyager_memes',
    'deepspacenine'
]

# startreksub = reddit.subreddit("+".join(subs))
startreksub = reddit.subreddit("testingground4bots")

def hasMoreQuotesCriteria(comment):
    parent = comment.parent()
    return moreQuotesRegex.search(comment.body.lower()) \
            and comment.author != redditUserName \
            and parent.author == redditUserName \
            and doesEmhReplyExist(comment) == False

def hasEmhCommented(CommentForest):
    for comment in CommentForest:
        if(comment.author == redditUserName):
            return True
        if(comment.replies.__len__() != 0):
            comment.replies.replace_more(None, 0)
            return hasEmhCommented(comment.replies)
        else:
            return False

def doesEmhReplyExist(comment):
    if comment.replies.__len__() == 0:
        return False
    else:
        for reply in comment.replies:
            if(reply.author == redditUserName):
                return True

def getEmhReply(comment):
    if comment.replies.__len__() == 0:
        return
    
    if comment.author == redditUserName:
        return comment

    for reply in comment.replies:
        if reply.author == redditUserName:
            return reply
    
def replyWithEMHQuote(comment):
    index = randrange(emhQuotes.__len__())
    quote = emhQuotes[index]['quote']
    episode = emhQuotes[index]['episodeName']
    url = emhQuotes[index]['url']
    contact = "\n\n\n\n^(Is this annoying? Can I do better? Tell my [creator](https://www.reddit.com/user/koloqial)!)"
    optout = "\n\n\n\n ^(If you wish for the EMH to not reply to you ever again, simply reply with 'optout')"
    reply = quote + "\n\n["+episode+"]("+url+")\n\n Ask me for more quotes or you can summon me!" + contact + optout

    # template = '''\ 
    # {quote}\n\n
    # ["+{episode}+"]("+{url}+")\n\n
    # Ask me for more quotes!\n\n\n\n
    # {contact}\n\n\n\n
    # {optout}
    # '''.format()

    comment.reply(body=reply)
    print("Replied to:" + comment.body)
    print("Replied with: "+reply)

def isUserOptingOut(comment, author):
    if author == redditUserName:
        return False
    return optOutRegex.search(comment) != None


def hasUserOptedOut(username):
    optoutList = getOptOutList()
    for user in optoutList:
        return True if user == username else False