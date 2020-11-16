from pymongo import MongoClient
from mongoengine import *
import datetime

db_uri = "mongodb+srv://project_user:7330@clusterbw.nwlcz.mongodb.net/BWCompany?retryWrites=true&w=majority"
db = connect("BWCompany", host=db_uri)



