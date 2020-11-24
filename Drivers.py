from mongoengine import *

class Hometown(EmbeddedDocument):
    city = StringField(required=True)
    state = StringField(required=True, max_length=2)
    def __get__(self):
        return([self.city,self.state])

class Drivers(Document):
    driver_id = StringField(required=True)
    fname = StringField(required=True)
    lname = StringField(required=True)
    age = IntField(required=True)
    home = EmbeddedDocumentField(Hometown)

    

