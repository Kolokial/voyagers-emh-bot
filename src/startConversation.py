from types import NoneType
from src.functions import *
import time


def startConversation(CommentForest):
    for comment in CommentForest:
        if isEmh(comment.author) == None:
            continue

        author = comment.author
        if (hasSubOptedOut(comment)):
            print(comment.subreddit.display_name, "has opted out")
            continue
        elif (isModOptingSubOut(comment)):
            print(comment.author.name, "is opting ",
                  comment.subreddit.display_name, "out")
            continue
        elif author != NoneType and hasUserOptedOut(author.name):
            print(comment.author.name, "has opting out")
            continue
        elif isUserOptingOut(comment.body, author):
            print(comment.author.name, "is opting out")
            insertIntoOptOutTable(author)
            continue

        # comment.refresh()
        # comment.replies.replace_more(limit=None, threshold=0)
        # print("Comment written by :", author)
        # print("replies", comment.replies.__len__())
        # print("comment", comment.body)
        # print("Id:", comment.id)
        if (doctorRegex.search(comment.body.lower()) is not None):
            print("found a comment mentioning the doctor")
            print("---------------------------------\n")
            print("Comment written by :", comment.author)
            print("replies", comment.replies.__len__())
            print("comment", comment.body)
            print("Id:", comment.id)
            print("permalink: ", comment.permalink)
            if (doesEmhReplyExist(comment) == False):
                print("with no previous replies")
                replyWithEMHQuote(comment)
                return

            if (comment.replies.__len__()):
                time.sleep(2)
                startConversation(comment.replies)


for post in startreksub.hot(limit=50):

    # post = reddit.submission(post.id)
    if hasEmhCommentedOnPost(post.id):
        continue
    print("--------------------------")
    print("Subreddit:", post.subreddit.display_name)
    print("Title: ", post.title)
    # print("Id:", post.id)
    # print("Text: ", post.selftext)
    # print("Comments: ", post.comments.__len__())
    while True:
        try:
            post.comments.replace_more()
            break
        except PossibleExceptions:
            print("Handling replace_more exception")
            sleep(5)
    if post.comments.__len__() == 0:
        continue

    if hasEmhCommented(post.comments) == False:
        startConversation(post.comments)
        time.sleep(2)
