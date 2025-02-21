from functions import *
def startConversation(CommentForest):
    for comment in CommentForest:
        if comment.author == None:
            continue
       
        author = comment.author.name
        if(hasSubOptedOut(comment)):
            print("Sub opted out!")
            continue
        elif(isModOptingSubOut(comment)):
            print("Sub is opting out!")
            continue
        elif hasUserOptedOut(author):
            print("User has opted out")
            continue
        elif isUserOptingOut(comment.body, author):
            print("User is opting out")
            insertIntoOptOutTable(author)
            continue

        #comment.refresh()
        #comment.replies.replace_more(limit=None, threshold=0)
        print("Comment written by :", author)
        print("replies", comment.replies.__len__())
        print("comment", comment.body)
        print("Id:", comment.id)
        if(doctorRegex.search(comment.body.lower()) is not None):
            print("found a comment mentioning the doctor")
            # print("---------------------------------\n")
            # print("Comment written by :", comment.author)
            # print("replies", comment.replies.__len__())
            #print("comment", comment.body)
            # print("Id:", comment.id)
            if(doesEmhReplyExist(comment) == False):
                print("with no previous replies")
                replyWithEMHQuote(comment)
                return
            
            if(comment.replies.__len__()):
                time.sleep(2)
                startConversation(comment.replies)

for submission in startreksub.new(limit=100):
    
    post = reddit.submission(submission.id)
    print("--------------------------")
    print("Title: ", submission.title)
    print("Id:", submission.id)
    print("Text: ", submission.selftext)
    print("Comments: ", post.comments.__len__())
    post.comments.replace_more(limit=None, threshold=0)
    if post.comments.__len__() == 0:
        continue

    if hasEmhCommented(post.comments) == False:
        startConversation(post.comments)
        time.sleep(2)
