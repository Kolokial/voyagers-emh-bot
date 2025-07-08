from time import sleep
from EMHModule.functions import *
from EMHModule.lookForMoreQuotes import lookForMoreQuotesRequest

# for post in startreksub.hot(limit=50):
comments = getEmhComments()
reddit = getRedditInstance()

for commentId in comments:
    comment = reddit.comment(commentId)
    
    comment.refresh()
    comment.replies.replace_more()
    # print("--------------------------")
    # print("Title: ", comment.title)
    # print("Id:", comment.id)
    # print("Text: ", comment.selftext)
    # print("Score: ", comment.score)
    while  comment.replies.__len__() > 0:    
        try:
            comment.replies.replace_more()
            lookForMoreQuotesRequest(comment.replies)
            break
        except PossibleExceptions:
            print("Handling replace_more exception")
            sleep(5)