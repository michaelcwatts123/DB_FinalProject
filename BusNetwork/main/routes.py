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
app.config["MONGO_URI"] = 'mongodb+srv://admin:FyJKue16fzF5et8v@cluster0.bbd6r.mongodb.net/BusNetwork?retryWrites=true&w=majority'
mongo = PyMongo(app)
app.config["FILE_UPLOADS1"] = './BusNetwork/static/uploads/driver'
app.config["FILE_UPLOADS2"] = './BusNetwork/static/uploads/routes'
app.config["FILE_UPLOADS3"] = './BusNetwork/static/uploads/Assignment'
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

def validate_assignment(obj):
    # Define Rest time between journeys.
    if not obj:
        print("No Assignment object to validate")
        return False
    else:
        route_assignment = Assignment.objects(driver_id=obj.driver_id)
        # Check constraints 1 & 2 for driver assignment
        for r in route_assignment:
            if r.weekDay == obj.weekDay:
                existing_route = Route.objects.get(routeNumber = r.routeNumber.id)
                potential_route = Route.objects.get(routeNumber = obj.routeNumber.id)
                rest_time = (existing_route.travelTimeHour*60 + existing_route.travelTimeMin)/2
                potential_departure = potential_route.departureHour*60 + potential_route.departureMin
                print(potential_departure)
                potential_arrival = potential_departure + potential_route.travelTimeHour*60 + potential_route.travelTimeMin
                print(potential_arrival)
                existing_departure = existing_route.departureHour*60 + existing_route.departureMin
                print(existing_departure)
                existing_arrival = existing_departure + existing_route.travelTimeHour*60 + existing_route.travelTimeMin
                print(existing_arrival)
                if potential_departure >= existing_departure and potential_departure <= existing_arrival:
                    print("Another route assignment exists in this time frame. Driver not available")
                    return False
                elif potential_departure < existing_departure and potential_arrival >= existing_departure:
                    print("Route assignment interferes with another departure.  Driver cannot be assigned this route")
                    return False
                elif potential_departure < existing_departure and potential_arrival <= existing_departure - rest_time:
                    print("Route assignment successful")
                    return True
                elif potential_departure >= existing_departure + rest_time:
                    print("Route assignment successful")
                    return True
            else:
                print("New day no issues")
                return True
            
    return True



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
                                Driver.save(x)
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
                        for line in open("Assignment.xlsx", encoding = "utf-8",errors='ignore'):
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


