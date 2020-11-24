from flask_mongoengine import Document
from mongoengine import IntField, DateTimeField, StringField, ReferenceField, ListField

class Driver(Document):
   # def __init__(self,id, fName, lName,age, city,state):
        id = StringField(primary_key=True)
        firstName = StringField(max_length=120, required=True, verbose_name="First name")
        lastName = StringField(max_length=120, required=True, verbose_name="Last name")
        age = IntField(min_value=0, max_value=None)
        city = StringField(max_length=120, required=True, verbose_name="City")
        state = StringField(max_length=120, required=True, verbose_name="State")

    #def __str__(self):
     #   return str(self.__dict__)

class Route(Document):
    #def __init__(self, rNumber, rName, depCity, depCityCode, destCity, destCode, rType, depTimeHours, depTimeMin, tTimeHours, tTimeMin):
        routeNumber =  StringField(primary_key=True)
        routeName = StringField(max_length=120, required=True, verbose_name="Route name")
        departureCity = StringField(max_length=120, required=True, verbose_name="Departure City")
        departureCode =  StringField(max_length=120, required=True, verbose_name="Departure Code")
        desinationCode =  StringField(max_length=120, required=True, verbose_name="Departure Code")
        routeType = StringField(max_length=120, required=True, verbose_name="Route Type")
        departureHour =  IntField(min_value=0, max_value=None)
        departureMin =  IntField(min_value=0, max_value=None)
        travelTimeHour =  IntField(min_value=0, max_value=None)
        travelTimeMin =  IntField(min_value=0, max_value=None)
        #totalDepartueTime = 60*int(departureHour) + int(travelTimeMin)
        #totalTime = int(travelTimeHour) * 60 + int(totalDepartueTime)
    
    #def __str__(self):
     #   return str(self.__dict__)

class Assignment(Document):
    #def __init__(self, id, route, weekDay):
        driver_id = ReferenceField(Driver, requiredfield=True)
        routeNumber = ReferenceField(Route, requiredfield=True)
        weekDay = StringField(max_length=120, required=True, verbose_name="Day of the Week")
        meta = { 'allow_inheritance': True,}
    #def __str__(self):
      # return str(self.__dict__)

