from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import pymongo
import sys
import os
import logging

load_dotenv()

uri = os.getenv('MONGODB_CONNECTION_STRING')
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    #logging.info(f"Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    logging.error(f"DB Connection Issue:", e)



# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  logging.info(f"An Invalid URI host error was received. Is your host name correct in your connection string?")
  sys.exit(1)

db = client.voyagersEMHBot

optout_table = db['user_optout']
subreddits_table = db['subreddits']
commented_posts_table = db['commented_posts']
emh_comments = db['emh_comments']

def insertIntoOptOutTable(username):
    try: 
        result = optout_table.insert_many([{"name": username}])

    # return a friendly error if the operation fails
    except pymongo.errors.OperationFailure:
        logging.error(f"An authentication error was received. Are you sure your database user is authorized to perform write operations?")
        sys.exit(1)
    else:
        inserted_count = len(result.inserted_ids)
        logging.info(f"I inserted %x documents." %(inserted_count))

        logging.info(f"\n")

def getOptOutList():
  result = optout_table.find()
  list = []
  if result:
      for doc in result:
        list.append(doc['name'])
  else:
    logging.info(f"No documents found.")
  return list

def optOutSubReddit(subredditName):
    try: 
      query_filter = { "name": subredditName }
      result = subreddits_table.delete_one(query_filter)
    except pymongo.errors.OperationFailure:
        logging.info(f"An authentication error was received. Are you sure your database user is authorized to perform write operations?")
        sys.exit(1)
    else:
        deleted_count = result.deleted_count
        logging.info(f"I deleted %x documents. {deleted_count}")

def getSubreddits():
  result = subreddits_table.find()
  list = []
  logging.info(result)
  if result:
      for doc in result:
        logging.info(doc)
        list.append(doc['name'].lower())
  else:
    logging.info(f"No documents found.")
  return list

def updatePostsCommentedOn(post_id):
  try: 
    query = { "post_id": post_id }
    result = commented_posts_table.insert_many([query])
    
  except pymongo.errors.OperationFailure:
    logging.info(f"An authentication error was received. Are you sure your database user is authorized to perform write operations?")
    sys.exit(1)
  else:
    inserted_count = len(result.inserted_ids)
    logging.info(f"I inserted %x documents." %(inserted_count))

def hasEmhCommentedOnPost(post_id):
  posts = commented_posts_table.find({"post_id": post_id})
  
  if posts:
      for post in posts:
        if post['post_id'] == post_id:
           return True;
  else:
    logging.info(f"EMH hasn't commented on found.", post_id)
  return False

def getPostsEmhHasCommentedOn():
  posts = commented_posts_table.find()
  list = []
  if posts:
      for post in posts:
        list.append(post['post_id'])
  else:
    logging.info(f"EMH hasn't commented on found.")
  return list


def updateEmhComments(comment_id):
  try: 
    query = { "comment_id": comment_id }
    result = emh_comments.insert_many([query])
    
  except pymongo.errors.OperationFailure:
    logging.info(f"An authentication error was received. Are you sure your database user is authorized to perform write operations?")
    sys.exit(1)
  else:
    inserted_count = len(result.inserted_ids)
    logging.info(f"I inserted %x documents." %(inserted_count))

def getEmhComments():
  comment_ids = emh_comments.find()
  list = []
  if comment_ids:
      for comment_id in comment_ids:
        list.append(comment_id['comment_id'])
  else:
    logging.info(f"EMH hasn't commented.")
  return list