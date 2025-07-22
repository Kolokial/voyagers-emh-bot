from  datetime import datetime
from time import sleep
from EMHModule.functions import getRedditInstance
from EMHModule.mongodb import getEmhComments
from EMHModule.lookForMoreQuotes import lookForMoreQuotesRequest
import logging
# for post in startreksub.hot(limit=50):
commentIds = getEmhComments()
reddit = getRedditInstance()

for commentId in commentIds:
    comment = reddit.comment(commentId)
    timestamp = int(comment.created_utc)
    time_since_comment_written = datetime.now() - datetime.fromtimestamp(timestamp)

    if(comment.locked | time_since_comment_written.days > 30):
        continue       
        
    comment.refresh()
    comment.replies.replace_more()
    # logging.info(f"--------------------------")
    # logging.info(f"Title: {comment.title}")
    # logging.info(f"Id:{comment.id}")
    # logging.info(f"Text: {comment.selftext}")
    # logging.info(f"Score: {comment.score}")
    while  comment.replies.__len__() > 0:    
        try:
            comment.replies.replace_more()
            lookForMoreQuotesRequest(comment.replies)
            break
        except PossibleExceptions:
            logging.info(f"Handling replace_more exception")
            sleep(5)