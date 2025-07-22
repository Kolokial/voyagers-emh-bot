
from datetime import time
from time import sleep
from EMHModule.functions import getListOfSubs, hasEmhCommented, startConversation, hasEmhCommentedOnPost
import logging

startreksub = getListOfSubs()

for post in startreksub.hot(limit=50):

    # post = reddit.submission(post.id)
    if hasEmhCommentedOnPost(post.id):
        continue
    logging.info(f"--------------------------")
    logging.info(f"Subreddit: {post.subreddit.display_name}")
    logging.info(f"Title:  {post.title}")
    logging.info(f"Id: {post.id}")
    logging.info(f"Comments:  {post.comments.__len__()}")
    while True:
        try:
            post.comments.replace_more()
            break
        except PossibleExceptions:
            logging.info(f"Handling replace_more exception")
            sleep(5)
    if post.comments.__len__() == 0:
        continue

    if hasEmhCommented(post.comments) == False:
        startConversation(post.comments)
        #sleep(1)