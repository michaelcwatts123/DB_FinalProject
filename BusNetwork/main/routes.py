from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask import Flask
import os, json, csv#, #models
from csv import reader
from .extensions import mongo
from flask_pymongo import PyMongo
from .models import Driver, Assignment, Route
from flask_mongoengine import MongoEngine
from mongoengine.queryset.visitor import Q
from json2html import *



app = Flask(__name__)
#app.config["MONGO_URI"] = 'mongodb+srv://admin:FyJKue16fzF5et8v@cluster0.bbd6r.mongodb.net/BusNetwork?retryWrites=true&w=majority'
app.config["MONGO_URI"] = 'mongodb+srv://project_user:7330@busnetwork.nwlcz.mongodb.net/BusNetwork?retryWrites=true&w=majority'
mongo = PyMongo(app)
app.config["FILE_UPLOADS1"] = './BusNetwork/static/uploads/driver'
app.config["FILE_UPLOADS2"] = './BusNetwork/static/uploads/routes'
app.config["FILE_UPLOADS3"] = './BusNetwork/static/uploads/Assignment'
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

def validate_driver(obj):
    if not obj:
        print("No driver object to be validated")
        return False
    else:
        route_set = Routes.objects(destinationCity=obj.city)
        if not route_set:
            print("No routes with the destination city as the Driver's hometown")
            return False
        else:
            print("Driver can be hired")
            return True



def validate_assignment(obj):
    if not obj:
        print("No Assignment object to validate")
        return False
    else:
        check_driver_dest = False
        day = ('s', 'M', 'T', 'W', 'U', 'F', 'S')
        route_assignment = Assignment.objects(driver_id=obj.driver_id)
        # Check constraints 1 & 2 for driver assignment
        if not route_assignment:
            print("No previous routes assigned.  Proceed with assignment")
            return True
        for r in route_assignment:
            existing_route = Route.objects.get(routeNumber = r.routeNumber.id)
            potential_route = Route.objects.get(routeNumber = obj.routeNumber.id)
            existing_driver_detail = Driver.objects.get(id = r.driver_id.id)
            potential_driver_detail = Driver.objects.get(id = obj.driver_id.id)
            rest_time = (existing_route.travelTimeHour*60 + existing_route.travelTimeMin)/2
            potential_departure = potential_route.departureHour*60 + potential_route.departureMin
            potential_arrival = potential_departure + potential_route.travelTimeHour*60 + potential_route.travelTimeMin
            potential_rest = (potential_route.travelTimeHour*60 + potential_route.travelTimeMin)/2  
            existing_departure = existing_route.departureHour*60 + existing_route.departureMin     
            existing_arrival = existing_departure + existing_route.travelTimeHour*60 + existing_route.travelTimeMin  
            if potential_driver_detail.city == potential_route.destinationCity:
                potential_rest = max(potential_rest, 18*60)
            if existing_route.destinationCity == potential_driver_detail.city:
                rest_time = max(rest_time, 18*60)
            old_route_end_day = day.index(r.weekDay)
            old_route_end_total = existing_route.departureHour*60 + existing_route.departureMin + existing_route.travelTimeHour*60 + existing_route.travelTimeMin + rest_time
            if old_route_end_total >= 1440:
                old_route_end_time = old_route_end_total % 1440 
                old_route_end_day += old_route_end_total//1440
            if old_route_end_day < day.index(obj.weekDay):
                print("No issues with this route")
                print(r.to_json())
                return True
            elif old_route_end_day == day.index(obj.weekDay):
                if potential_departure <= existing_arrival + rest_time:
                    print("Route cannot be assigned before existing route ends")
                    return False
                print("Route assignment without collision possible")
                return True
            elif old_route_end_day > day.index(obj.weekDay):
                print ("New route cannot be assigned before old route assignment ends")
                return False
            elif day.index(r.weekDay) > day.index(obj.weekDay):
                potential_route_end_total = potential_arrival + potential_rest
                if potential_route_end_total >= 1440:
                    potential_route_end_time = potential_route_end_total%1440
                    potential_route_end_day = day.index(r.weekDay) + potential_route_end_total//1440
                if potential_route_end_day == day.index(r.weekDay):
                    if potential_route_end_time >= existing_departure:
                        print("The new assignment will not end before the departure of an existing route")
                        return False
                print("New route can be assigned without any collision")
                return True

def check_driver_hometown_assigned():
    deleted_drivers = []
    for drivers in Driver.objects:
        if not drivers:
            print("No drivers in record")
            exit
        check_dest = False
        route_assignments = Assignment.objects(driver_id=drivers.id)
        if not route_assignments:
            print("No route assignments for the particular driver")
            exit
        for route in route_assignments:
            assigned_route = Route.objects.get(routeNumber=route.routeNumber.id)
            if assigned_route.destinationCity == drivers.city:
                check_dest = True
            
        if not check_dest:
            deleted_drivers.append(drivers.id)
            Assignment.objects(driver_id=drivers.id).delete()
            drivers.delete()
    return deleted_drivers



@main.route("/upload-docs", methods=["GET", "POST"])
def upload_docs():
    
    if request.method == "POST":

        if request.files:

            file = request.files.getlist("files")
            data=[]
            driver_collection = mongo.db.driver
            for fil in file:
                if not fil:
                    print("No file")
                    return ('',204)
                elif fil.filename == 'Driver.csv':
                    fil.save(os.path.join(app.config["FILE_UPLOADS1"], fil.filename))
                    with open(fil.filename, 'r') as f:
                        for line in open("Driver.csv"):
                            #data = f.read()
                            csv_row=[row for row in csv.reader(f.read().splitlines())]
                            for csv_row in csv_row:
                                x=Driver(id=csv_row[0],firstName=csv_row[1],lastName=csv_row[2],age =csv_row[3],city =csv_row[4],state =csv_row[5])
                                print(x.id)
                                #driver_collection.insert(json.dumps(x))
                                if validate_driver(x):
                                    print("Driver validated")
                                    Driver.save(x)
                                else:
                                    print("Driver cannot be hired")
                                    continue
                        #driver_collection.save(Driver())
                    
                elif fil.filename == 'Routes.csv':
                    fil.save(os.path.join(app.config["FILE_UPLOADS2"], fil.filename))
                    with open(fil.filename, 'r') as f:
                        for line in open("Routes.csv"):
                            #data = f.read()
                            csv_row=[row for row in csv.reader(f.read().splitlines())]
                            for csv_row in csv_row:
                                y=Route(routeNumber=csv_row[0],routeName=csv_row[1],departureCity=csv_row[2],departureCode =csv_row[3],destinationCity =csv_row[4],desinationCode =csv_row[5],routeType =csv_row[6],departureHour =csv_row[7],departureMin =csv_row[8],travelTimeHour =csv_row[9],travelTimeMin =csv_row[10])
                                print(y.id)
                                #driver_collection.insert(json.dumps(x))
                                Route.save(y)
                elif fil.filename == 'Assignment.csv' or fil.filename == 'Assignment.xlsx':
                    fil.save(os.path.join(app.config["FILE_UPLOADS3"], fil.filename))
                    with open(fil.filename, 'r', encoding = "utf-8") as f:
                        for line in open("Assignment.csv", encoding = "utf-8",errors='ignore'):
                            #data = f.read()
                            csv_row=[row for row in csv.reader(f.read().splitlines())]
                            for csv_row in csv_row:
                                z=Assignment(driver_id=csv_row[0],routeNumber=csv_row[1],weekDay=csv_row[2])
                                print(z.weekDay)
                                #driver_collection.insert(json.dumps(x))
                                if validate_assignment(z):
                                    print("Driver Assignment Validated")
                                    Assignment.save(z)
                                else:
                                    print("Driver Assignment not possible")
                                    continue
                    deleted_driver_list = check_driver_hometown_assigned()
                    print("Following drivers are deleted for not getting assigned a destination route")
                    print(deleted_driver_list)
            return redirect(request.url)
    return render_template("index.html")

@main.route('/driver_lookup', methods=['POST'])
def driver_lookup():
    driver_fn = request.form.get('driver_fn')
    driver_ln = request.form.get('driver_ln')
    driver_fulln = driver_fn+ ' '+driver_ln
    print(driver_fulln)
    driver_results= Driver.objects(Q(firstName=driver_fn) & Q(lastName=driver_ln))
    driver_id=[]
    for rt in driver_results:
        driver_id.append(rt.id)
    print(driver_id)            
    driver_routes = Assignment.objects.filter(driver_id__in=driver_id)
    dr_rt=[]
    test=list(mongo.db.assignment.find({"driver_id":{"$in":driver_id}}, {'_id': False,'_cls': False,'driver_id':False}))
    for t in test:
        dr_rt.append(t)
    print(dr_rt)
#    data=json2html.convert(driver_results.to_json())+json2html.convert(test)
    data=json2html.convert(driver_results.to_json())+json2html.convert(test)
    if not driver_results:
        return jsonify({'error': 'data not found'})
    else:
        return render_template('base.html', data=data)
    #return jsonify(driver_fn)


@main.route('/city_lookup', methods=['POST'])
def city_lookup():
    city_dest = request.form.get('city_lookup')
    city_results= Route.objects((Q(departureCity=city_dest)) | (Q(destinationCity=city_dest)))
    data=json2html.convert(city_results.to_json())
    if not city_results:
        return jsonify({'error': 'data not found'})
    else:
       return render_template('base.html', data=data)


@main.route('/route_lookup', methods=['POST'])
def route_lookup():
    route_exist = request.form.get('route_lookup')
    route_results=list(mongo.db.assignment.aggregate([{ "$match":{"routeNumber":route_exist}},
    { "$lookup": {
    "localField": "routeNumber",
    "from": "route",
    "foreignField": "_id",
    "as": "RouteInfo"
  } },
  {
        "$lookup":{
            "from": "driver", 
            "localField": "driver_id", 
            "foreignField": "_id",
            "as": "driver_info"
        }
    },
    {   
        "$project":{
            '_id':0,
            'routeNumber' : 1,
            'weekDay' : 1,
            'RouteInfo.routeName':1,
            'RouteInfo.departureCity':1,
            'RouteInfo.destinationCity':1,
            'RouteInfo.routeType':1,
            'RouteInfo.departureHour':1,
            'RouteInfo.departureMin':1,
            'RouteInfo.travelTimeHour':1,
            'RouteInfo.travelTimeMin':1,
            'driver_info.driver_id': 1,
            'driver_info.firstName':1,
            'driver_info.lastName':1,
            'driver_info.age':1,
            'driver_info.city':1,
            'driver_info.state':1
        } 
    }
  ]))
    route_details=list(mongo.db.route.find({"_id":route_exist}))
    for document in route_details:
        print(document)
    for document in route_results:
        print(document)
    if not route_results:
        return jsonify({'error': 'data not found'})
    else:
        return render_template('route.html', route=route_details, data=route_results)


@main.route('/route_exist_lookup', methods=['POST'])
def route_exist_lookup():
    route_exist_dept = request.form.get('route_exist_dept')
    route_exist_dest = request.form.get('route_exist_dest')
    route_exists_results= Route.objects(departureCity=route_exist_dept, destinationCity=route_exist_dest )
    route_results=list(mongo.db.route.aggregate([{ "$match":{ "$and":[{"departureCity":route_exist_dept},{"destinationCity":route_exist_dest}]}},
    { "$lookup": {
    "localField": "_id",
    "from": "assignment",
    "foreignField": "routeNumber",
    "as": "RouteInfo"
  } },
  {
        "$lookup":{
            "from": "driver", 
            "localField": "RouteInfo.driver_id", 
            "foreignField": "_id",
            "as": "driver_info"
        }
    },
    {   
        "$project":{
            'routeName':1,
            'departureCity':1,
            'destinationCity':1,
            'routeType':1,
            'departureHour':1,
            'departureMin':1,
            'travelTimeHour':1,
            'travelTimeMin':1,
            '_id':0,
            'routeNumber' : 1,
            'RouteInfo.weekDay' : 1,
            'driver_info.driver_id': 1,
            'driver_info.firstName':1,
            'driver_info.lastName':1,
            'driver_info.age':1,
            'driver_info.city':1,
            'driver_info.state':1
        } 
    }
  ]))
    data=(json2html.convert(route_exists_results.to_json()))
    if not route_exists_results:
        return jsonify({'error': 'data not found'})
    else:
        return render_template('route_exist.html', data=route_results)

@main.route('/route_exist_day_lookup', methods=['POST'])
def route_exist_day_lookup():
    route_exist_day_dept = request.form.get('route_exist_day_dept')
    route_exist_day_dest = request.form.get('route_exist_day_dest')
    if not request.form.get('route_exist_day_day'):
        print('no day selected')
        return ('',204)
    else:
        route_exist_day_day = request.form.get('route_exist_day_day')    
    print(route_exist_day_dept+' '+route_exist_day_dest+' '+route_exist_day_day)
    route_exists_results= Route.objects.filter((Q(departureCity=route_exist_day_dept)) | (Q(destinationCity=route_exist_day_dest)) )#.save()
    print(jsonify(route_exists_results.to_json()))
    routes=[]
    for rt in route_exists_results:
        routes.append(rt.routeNumber)
    print(routes)            
    route_exists_day = Assignment.objects.filter(routeNumber__in=routes, weekDay=route_exist_day_day)
    data=(json2html.convert(route_exists_day.to_json()))#jsonify(route_exists_day.to_json())
    if not route_exists_day:
        return jsonify({'error': 'data not found'})
    else:
        return render_template('base.html', data=data)


