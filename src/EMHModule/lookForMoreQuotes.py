import time

from EMHModule.functions import hasSubOptedOut, isModOptingSubOut, hasUserOptedOut,  isUserOptingOut, hasMoreQuotesCriteria, replyWithEMHQuote
from EMHModule.mongodb import insertIntoOptOutTable
import logging

def lookForMoreQuotesRequest(CommentForest):
    for comment in CommentForest:
        if comment.author == None:
            continue

        author = comment.author.name

        if (hasSubOptedOut(comment)):
            logging.info(f"{comment.subreddit.display_name} has opted out")
            continue
        elif (isModOptingSubOut(comment)):
            logging.info(f"{comment.author.name} is opting {comment.subreddit.display_name} out")
            continue
        elif hasUserOptedOut(author):
            logging.info(f"{comment.author.name} has opting out")
            continue
        elif isUserOptingOut(comment.body, author):
            logging.info(f"{comment.author.name} is opting out")
            insertIntoOptOutTable(author)
            continue
        elif hasMoreQuotesCriteria(comment):
            replyWithEMHQuote(comment)
        elif comment.replies.__len__() >= 1:
            time.sleep(2)
            lookForMoreQuotesRequest(comment.replies)



