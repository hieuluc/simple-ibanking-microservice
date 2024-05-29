
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

load_dotenv() 

uri =  os.getenv("MONGODB_URL")

# Create a new client and connect to the server
client = MongoClient(uri)

db = client.tutionService

tutionsCollection = db['tutions']

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)