from functions import *

def lookForMoreQuotesRequest(CommentForest):
    for comment in CommentForest:
        if comment.author == None:
            continue
       
        author = comment.author.name
                
        if(hasSubOptedOut(comment)):
            print(comment.subreddit.display_name, "has opted out")
            continue
        elif(isModOptingSubOut(comment)):
            print(comment.author.name, "is opting ", comment.subreddit.display_name, "out")
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

for submission in startreksub.hot(limit=100):
    
    #submission.comments.replace_more(limit=None, threshold=0)
    post = reddit.submission(submission.id)
    # print("--------------------------")
    # print("Title: ", submission.title)
    # print("Id:", submission.id)
    # print("Text: ", submission.selftext)
    # print("Score: ", submission.score)
    # print("Comments:", post.num_comments)
    while True:
        try:
            post.comments.replace_more()
            break
        except PossibleExceptions:
            print("Handling replace_more exception")
            sleep(5)

    if post.num_comments == 0:
        continue

    lookForMoreQuotesRequest(post.comments)
    time.sleep(2)