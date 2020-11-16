from mongoengine import *
import datetime

class DepartureData(EmbeddedDocument):
    city_name = StringField()
    city_code = StringField(max_length=2)

class DestinationData(EmbeddedDocument):
    city_name = StringField()
    city_code = StringField(max_length=2)

class DepartureTime(EmbeddedDocument):
    time_hrs = IntField(required=True)
    time_mins = IntField(required=True)

class TravelTime(EmbeddedDocument):
    time_hrs = IntField(required=True)
    time_mins = IntField(required=True)   

class Routes(Document):
    route_num = StringField(required=True)
    route_name = StringField(required=False, default='')
    departure_data = EmbeddedDocumentField(DepartureData)
    destination_data = EmbeddedDocumentField(DestinationData)
    route_type = IntField(required=True)
    departure_time = EmbeddedDocumentField(DepartureTime)
    travel_time = EmbeddedDocumentField(TravelTime)





    