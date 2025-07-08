
from EMHModule.mongodb import hasEmhCommentedOnPost


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