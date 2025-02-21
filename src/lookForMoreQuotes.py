from src.functions import *
import time


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


# for post in startreksub.hot(limit=50):
comments = getEmhComments()

for commentId in comments:
    comment = reddit.comment(commentId)
    # print("--------------------------")
    # print("Title: ", comment.title)
    # print("Id:", comment.id)
    # print("Text: ", comment.selftext)
    # print("Score: ", comment.score)
    if comment.replies.__len__() > 0:
        while True:
            try:
                comment.replies.replace_more()
                lookForMoreQuotesRequest(comment.replies)
                break
            except PossibleExceptions:
                print("Handling replace_more exception")
                sleep(5)
