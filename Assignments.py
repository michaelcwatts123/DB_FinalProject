from mongoengine import *
from Drivers import Drivers
from Routes import Routes

class Assignments(Document):
    driver = ReferenceField(Drivers)
    route = ReferenceField(Routes)
    day_of_week = StringField()
