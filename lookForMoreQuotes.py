from functions import *

def lookForMoreQuotesRequest(CommentForest):
    for comment in CommentForest:
        if hasUserOptedOut(comment.author.name):
            continue
        elif isUserOptingOut(comment.body, comment.author.name):
            insertIntoOptOutTable(comment.author.name)
            continue
        elif hasMoreQuotesCriteria(comment):
            replyWithEMHQuote(comment)
        elif comment.replies.__len__() >= 1:
            lookForMoreQuotesRequest(comment.replies)

for submission in startreksub.hot(limit=100):
    
    #submission.comments.replace_more(limit=None, threshold=0)
    post = reddit.submission(submission.id)
    # print("--------------------------")
    # print("Title: ", submission.title)
    # print("Id:", submission.id)
    # print("Text: ", submission.selftext)
    # print("Score: ", submission.score)
    # print("Comments:", post.num_comments)
    post.comments.replace_more(limit=None, threshold=0)
    if post.num_comments == 0:
        continue

    lookForMoreQuotesRequest(post.comments)
