import time

from EMHModule.functions import hasMoreQuotesCriteria, hasSubOptedOut, hasUserOptedOut, isModOptingSubOut, isUserOptingOut, replyWithEMHQuote
from EMHModule.mongodb import insertIntoOptOutTable


def lookForMoreQuotesRequest(CommentForest):
    for comment in CommentForest:
        if comment.author == None:
            continue

        author = comment.author.name

        if (hasSubOptedOut(comment)):
            print(comment.subreddit.display_name, "has opted out")
            continue
        elif (isModOptingSubOut(comment)):
            print(comment.author.name, "is opting ",
                  comment.subreddit.display_name, "out")
            continue
        elif hasUserOptedOut(author):
            print(comment.author.name, "has opting out")
            continue
        elif isUserOptingOut(comment.body, author):
            print(comment.author.name, "is opting out")
            insertIntoOptOutTable(author)
            continue
        elif hasMoreQuotesCriteria(comment):
            replyWithEMHQuote(comment)
        elif comment.replies.__len__() >= 1:
            time.sleep(2)
            lookForMoreQuotesRequest(comment.replies)



