from EMHModule.functions import hasMoreQuotesCriteria, replyWithEMHQuote, shouldSkipComment


def lookForMoreQuotesRequest(commentForest):
    for comment in commentForest:
        if not shouldSkipComment(comment) and hasMoreQuotesCriteria(comment):
            replyWithEMHQuote(comment)
        elif len(comment.replies) > 0:
            lookForMoreQuotesRequest(comment.replies)
