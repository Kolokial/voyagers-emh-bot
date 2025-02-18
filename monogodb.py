from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import sys
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv('MONGODB_CONNECTION_STRING')

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)



# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
  sys.exit(1)

# use a database named "myDatabase"
db = client.voyagersEMHBot

optout_table = db['user_optout']


def insertIntoOptOutTable(username):
    try: 
        result = optout_table.insert_many([{"name": username}])

    # return a friendly error if the operation fails
    except pymongo.errors.OperationFailure:
        print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
        sys.exit(1)
    else:
        inserted_count = len(result.inserted_ids)
        print("I inserted %x documents." %(inserted_count))

        print("\n")

def getOptOutList():
  result = optout_table.find()
  list = []
  if result:
      for doc in result:
        list.append(doc['name'])
  else:
    print("No documents found.")
    print("\n")
  return list