from pymongo import MongoClient
from mongoengine import *
import datetime
from Drivers import *
from Routes import *
from Assignments import *


db_uri = "mongodb+srv://project_user:7330@clusterbw.nwlcz.mongodb.net/BWCompany?retryWrites=true&w=majority"
db = connect("BWCompany", host=db_uri)

driver_test = Drivers(driver_id = "ABC123",
                      fname = "Batman",
                      lname = "Robin",
                      age = 32).save()
hometown_test = Hometown(city = "Dallas", state = "TX")
driver_test.home = hometown_test
driver_test.save()

route_test = Routes(route_num="interstate",
                    route_name="I35",
                    route_type=1).save()
dep_data = DepartureData(city_name = "Dallas",city_code="TX")
route_test.departure_data = dep_data
dest_data = DestinationData(city_name="Austin",city_code="AX")
route_test.destination_data = dest_data
dep_time = DepartureTime(time_hrs=12, time_mins=15)
route_test.departure_time = dep_time
travel = TravelTime(time_hrs=3,time_mins=30)
route_test.travel_time = travel
route_test.save()

assignmnet_test = Assignments(driver=driver_test,route=route_test,day_of_week="Sunday")
assignmnet_test.save()

driver_fname = input("Enter the First Name of the driver : ")
driver_lname = input("Enter the Last Name of the driver : ")
driver_obj = Drivers.objects(fname=driver_fname, lname=driver_lname)

for i in driver_obj:
    print("Driver Details : ")
    print(dict(i.to_mongo()))
  
assignment_obj = Assignments.objects(driver=i)
for i in assignment_obj:
    print(dict(i.to_mongo()))

    



