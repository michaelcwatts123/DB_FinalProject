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

from datetime import datetime


app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://admin:FyJKue16fzF5et8v@cluster0.bbd6r.mongodb.net/BusNetwork?retryWrites=true&w=majority'
#app.config["MONGO_URI"] = 'mongodb+srv://project_user:7330@busnetwork.nwlcz.mongodb.net/BusNetwork?retryWrites=true&w=majority'
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
        return False
    else:
        route_set = Route.objects(destinationCity=obj.city)
        if not route_set:
            return False
        else:
            return True



def validate_assignment(obj):
    if not obj:
        print("No Assignment object to validate")
        return False
    else:
        check_driver_dest = False
        day = ('s', 'M', 'T', 'W', 'U', 'F', 'S')
        try:
            route_assignment = Assignment.objects(driver_id=obj.driver_id)
            # Check if new route has to be assigned
            if not route_assignment:
                return True
            if(Assignment.objects(Q(driver_id=obj.driver_id)&Q(routeNumber=obj.routeNumber)&Q(weekDay=obj.weekDay))):
                print("Assignment already exists",obj.driver_id.id)
                return False
            # Validation check if existing route assignments or the potential assignment interferes with constraints
            for r in route_assignment:
                existing_route = Route.objects.get(routeNumber = r.routeNumber.id)
                potential_route = Route.objects.get(routeNumber = obj.routeNumber.id)
                if potential_route.routeType == '1':
                    if obj.weekDay=='s' or obj.weekDay=='S':
                        print("Route assignment weekDay = "+obj.weekDay+"inconsistent with Route Type: "+potential_route.routeType)
                        return False
                elif potential_route.routeType == '2':
                    if 0 < day.index(obj.weekDay) < 6:
                        print("Route assignment weekDay inconsistent with Route Type")
                        return False
                existing_driver_detail = Driver.objects.get(id = r.driver_id.id)
                potential_driver_detail = Driver.objects.get(id = obj.driver_id.id)
                # Converting the times to minutes starting from 0 and ending at 1440 (24*60) minutes for the day
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
                    return True
                elif old_route_end_day == day.index(obj.weekDay):
                    if potential_departure <= existing_arrival + rest_time:
                        print("New route "+potential_route.routeNumber+ " cannot be assigned before existing route "+existing_route.routeNumber+ " ends")
                        return False
                    print("Route assignment without collision possible")
                    return True
                elif old_route_end_day > day.index(obj.weekDay):
                    print("New route "+potential_route.routeNumber+ " cannot be assigned before existing route "+existing_route.routeNumber+ " ends")
                    return False
                elif day.index(r.weekDay) > day.index(obj.weekDay):
                    potential_route_end_total = potential_arrival + potential_rest
                    if potential_route_end_total >= 1440:
                        potential_route_end_time = potential_route_end_total%1440
                        potential_route_end_day = day.index(r.weekDay) + potential_route_end_total//1440
                    if potential_route_end_day == day.index(r.weekDay):
                        if potential_route_end_time >= existing_departure:
                            print("The new route "+potential_route.routeNumber+ "  will not end before the departure of existing route " + existing_route.routeNumber)
                            return False
                    return True
        except Exception as e:
            print(e)
            return False

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
            continue
        for route in route_assignments:
            assigned_route = Route.objects.get(routeNumber=route.routeNumber.id)
            if assigned_route.destinationCity == drivers.city:
                check_dest = True          
        if not check_dest:
            deleted_drivers.append(drivers.id)
            Assignment.objects(driver_id=drivers.id).delete()
            drivers.delete()
    return deleted_drivers

def routeCheck(start, end, day):
    route_exist_day_dept = start
    route_exist_day_dest = end
    route_exist_day_day = day
    
    route_exists_results= Route.objects.filter((Q(departureCity=route_exist_day_dept)) | (Q(destinationCity=route_exist_day_dest)) )
    routes=[]
    for rt in route_exists_results:
        routes.append(rt.routeNumber)
    route_exists_day = Assignment.objects.filter(routeNumber__in=routes, weekDay=route_exist_day_day)
    if not route_exists_day:
        return None
    else:
        return route_exists_day
        

def validate_constraint3():
    assignmentsToRemove = list()
    drivers = Driver.objects.only('id')
    uniqueDrivers = []
    for i in drivers:
        uniqueDrivers.append(i.id)
    uniqueDrivers = list(set(uniqueDrivers))
    for i in uniqueDrivers:
        print(i)
        vals = OrderedDict()
        vals['s'], vals['M'], vals['T'], vals['W'], vals['U'], vals['F'], vals['S'] = [],[],[],[],[],[],[]
        assignments_results = Assignment.objects(Q(driver_id=i))
        daysOfTheWeek = {'s':['M','T'],'M':['T','W'],'T':['W','U'],'W':['U','F'],'U':['F','S'],'F':['S','s'],'S':['s','M']}
        ptr = 0
        for j in assignments_results:
            routes = Route.objects(Q(routeNumber=j.routeNumber.id)).order_by('+departureHour','+departureMin')
            for r in routes:
               vals[j.weekDay].append(json.loads(r.to_json()))

        for j in vals.keys():
            if vals[j]:
                nextTrips = []
                nextDays = [j]
                for k in daysOfTheWeek[j]:
                    nextDays.append(k)
                    if(vals[k]):
                        nextTrips.append((vals[k][-1], nextDays))
                    if nextTrips:
                        if(vals[j][0]['destinationCity'].strip() != nextTrips[-1][0]['departureCity'].strip()):
                            removalFlag = True
                            for k in nextTrips[-1][1]:
                                trip = routeCheck(vals[j][0]['destinationCity'], nextTrips[-1][0]['departureCity'], k)
                                if trip:

                                    badRouteFlag = False
                                    start, end = trip[0], trip[len(trip)-1]
                                    if start.weekDay == j:
                                        start = json.loads(Route.objects(Q(routeNumber=start.routeNumber.id)).to_json())[0]
                                        sTime = datetime.strptime(str(start['departureHour']) +':'+str(start['departureMin']),'%H:%M')
                                        eTimeH = vals[j][0]['departureHour'] + vals[j][0]['travelTimeHour']
                                        eTimeM = vals[j][0]['departureMin'] + vals[j][0]['travelTimeMin']
                                        if(eTimeM >= 60):
                                            eTimeH+= 1
                                            eTimeM -=60
                                        if(eTimeH >= 24):
                                            badRouteFlag = True
                                            break
                                        eTimeH = str(eTimeH)
                                        eTimeM = str(eTimeM)
                                        eTime = str(eTimeH) + ':' +str(eTimeM)
                                        eTime = datetime.strptime(eTime,'%H:%M')
                                        if(sTime > eTime):
                                            badRouteFlag = True
                                            break
#                                        pprint.pprint(sTime)
                                    if end.weekDay == nextDays[-1]:
                                        end = json.loads(Route.objects(Q(routeNumber=end.routeNumber.id)).to_json())[0]
                                        sTime = datetime.strptime(str(nextTrips[-1][0]['departureHour']) +':'+str(nextTrips[-1][0]['departureMin']),'%H:%M')
                                        eTimeH = end['departureHour'] + end['travelTimeHour']
                                        eTimeM = end['departureMin'] + end['travelTimeMin']
                                        if(eTimeM >= 60):
                                            eTimeH+= 1
                                            eTimeM -=60
                                        if(eTimeH >= 24):
                                            badRouteFlag = True
                                            break
                                        eTimeH = str(eTimeH)
                                        eTimeM = str(eTimeM)
                                        eTime = str(eTimeH) + ':' +str(eTimeM)
                                        eTime = datetime.strptime(eTime,'%H:%M')
                                        if(sTime < eTime):
                                            badRouteFlag = True
                                            break
                                    if not badRouteFlag:
                                        removalFlag = False
                                        break
                            if removalFlag:
                                assignmentsToRemove.append((i, nextTrips[-1][0]['_id'], nextTrips[0][1][-1]))
                            else:
                                break
                        else:
                            break
    
#        pprint.pprint(vals)
#    print('The Following Assignments have been deleted for violating constraints')
#    pprint.pprint(assignmentsToRemove)
    if(len(assignmentsToRemove) > 0):
        for i in assignmentsToRemove:
            Assignment.objects.filter(driver_id=i[0],routeNumber=i[1], weekDay=i[2]).delete()
        validate_constraint3()


@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html')

@main.errorhandler(500)
def internal_error(error):
    return render_template('404.html')


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
                                    Driver.save(x)
                                else:
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
                                if not Driver.objects(Q(id=csv_row[0])):
                                    continue
                                if not Route.objects(Q(routeNumber=csv_row[1])):
                                    continue
                                z=Assignment(driver_id=csv_row[0],routeNumber=csv_row[1],weekDay=csv_row[2])
                                #driver_collection.insert(json.dumps(x))
                                if validate_assignment(z):
                                    Assignment.save(z)
                                else:
                                    continue
                    deleted_driver_list = check_driver_hometown_assigned()
                    print("Following drivers are deleted for not getting assigned a destination route")
                    print(deleted_driver_list)
            validate_constraint3()
            return redirect(request.url)
    return render_template("index.html")

@main.route('/driver_lookup', methods=['POST'])
def driver_lookup():
    driver_fn = request.form.get('driver_fn').capitalize()
    driver_ln = request.form.get('driver_ln').capitalize()
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
        return render_template('404.html')
    else:
        return render_template('base.html', data=data)
    #return jsonify(driver_fn)


@main.route('/city_lookup', methods=['POST'])
def city_lookup():
    days = ('s', 'M', 'T', 'W', 'U', 'F', 'S')
    city_dest = request.form.get('city_lookup').capitalize()
    data = ""
    for day in days:
        departure_results = {}
        destination_results = {}
        day_assignment = Assignment.objects(weekDay=day)
        for a in day_assignment:
            route_result = Route.objects.get(routeNumber=a.routeNumber.id)
            if route_result.departureCity==city_dest:
                if route_result.routeNumber not in departure_results:
                    departure_results[route_result.routeNumber]=route_result.departureHour*60+route_result.departureMin
            elif route_result.destinationCity==city_dest:
                if route_result.routeNumber not in destination_results:
                    destination_results[route_result.routeNumber]=route_result.departureHour*60+route_result.departureMin
        departure_results = sorted(departure_results, key=departure_results.__getitem__)
        destination_results = sorted(destination_results, key=destination_results.__getitem__)
        dep_city_results = Route.objects(routeNumber__in=departure_results).to_json()
        dest_city_results = Route.objects(routeNumber__in=destination_results).to_json()
        if departure_results or destination_results:
            data += "Routes through "+ city_dest + " for the day : " + day
        data +=json2html.convert(dep_city_results) + json2html.convert(dest_city_results)
    if data =="":
        return render_template('404.html')
    else:
        return render_template('base.html', data=data)


@main.route('/route_lookup', methods=['POST'])
def route_lookup():
    route_exist = request.form.get('route_lookup')
    route_results=list(mongo.db.assignment.aggregate([{ "$match":{"routeNumber":route_exist}},{ "$lookup": {
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
        return render_template('404.html')
    else:
        return render_template('route.html', route=route_details, data=route_results)

@main.route('/route_exist_lookup', methods=['POST'])
def route_exist_lookup():
    route_exist_dept = request.form.get('route_exist_dept').capitalize()
    route_exist_dest = request.form.get('route_exist_dest').capitalize()
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
            "let": { "id": "$Routeinfo.driver_id"},

            "pipeline": [
              {"$match":
                    {"$expr":{
                      "$eq" : ["$id", "$$id"]
                    }
                  },
                  
                },
                {
                  "$project" : {"RouteInfo.weekDay":1, "firstName": 1, "lastName": 1, "_id": 0}
                }],
              
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
            #'_id':1,
            'routeNumber' : 1,
            'RouteInfo.weekDay' : 1,
            'RouteInfo.driver_id' : 1,
            'driver_info.driver_id': 1,
            'driver_info.firstName':1,
            'driver_info.lastName':1,
            'driver_info.age':1,
            'driver_info.city':1,
            'driver_info.state':1
        } 
    }
  ]))
    print(route_results)
    assign_routes = Route.objects.filter(departureCity=route_exist_dept,destinationCity=route_exist_dest)
    routes=[]
    for rt in assign_routes:
        routes.append(rt.id)
    print(routes)
	
    route_results2=list(mongo.db.assignment.aggregate([{ "$match":{ "routeNumber":{"$in":routes}}},{ "$lookup": {
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
            'driver_info.driver_id': 1,
            'driver_info.firstName':1,
            'driver_info.lastName':1,
            'driver_info.age':1,
            'driver_info.city':1,
            'driver_info.state':1
        } 
    }
  ]))
    print(route_results2)
 
    data=(json2html.convert(route_exists_results.to_json()))
    if not route_exists_results:
        return render_template('404.html')
    else:
        return render_template('route_exist.html', data=route_results, routes=route_results2)

@main.route('/route_exist_day_lookup', methods=['POST'])
def route_exist_day_lookup():
    route_exist_day_dept = request.form.get('route_exist_day_dept').capitalize()
    route_exist_day_dest = request.form.get('route_exist_day_dest').capitalize()
    if not request.form.get('route_exist_day_day'):
        print('no day selected')
        return ('',204)
    else:
        route_exist_day_day = request.form.get('route_exist_day_day')    
    print(route_exist_day_dept+' '+route_exist_day_dest+' '+route_exist_day_day)
    route_exists_direct= Route.objects.filter((Q(departureCity=route_exist_day_dept)) & (Q(destinationCity=route_exist_day_dest)) )#.save()
    routes_direct=[]
    for rt in route_exists_direct:
        routes_direct.append(rt.routeNumber)
    print(routes_direct)       
    route_exists_direct_day = Assignment.objects.filter(routeNumber__in=routes_direct, weekDay=route_exist_day_day)
    route_results1=list(mongo.db.route.find({ "_id":{"$in":routes_direct}},{'_id': True,'routeName': True,'_id': True,'departureCity': True,'departureCode': True,'destinationCity': True,'desinationCode': True,'departureHour':True, 'departureMin': True,'travelTimeHour': True,'travelTimeMin': True}))
    data_direct=(json2html.convert(route_exists_direct_day.to_json()))

    route_exists_indirect= Route.objects.filter((Q(departureCity=route_exist_day_dept)) | (Q(destinationCity=route_exist_day_dest)) )#.save()
    routes_indirect=[]
    for rt in route_exists_indirect:
        routes_indirect.append(rt.routeNumber)
    print(routes_indirect)
    i=[]
    x=[]
    for j in route_exists_indirect:
        if ((j.destinationCity !=route_exist_day_dest) and (j.departureCity ==route_exist_day_dept)):
            i.append(j.destinationCity)
            x.append(j.routeNumber)
    print(i) 
    o=[]
    for j in route_exists_indirect:
        if ((j.departureCity !=route_exist_day_dept) and (j.destinationCity ==route_exist_day_dest)):
            o.append(j.departureCity)
            x.append(j.routeNumber)
    print(o)
    indirect_routes=[]
    for z in i: 
        route_exists_indirect= Route.objects.filter((Q(departureCity=i[0])) & (Q(destinationCity=o[0])) )
        for k in route_exists_indirect:
            indirect_routes.append(k.routeNumber)
            x.append(k.routeNumber)
    print(indirect_routes)
    print(x)
    indir_results=list(mongo.db.routes.find({"routeNumber":{"$in":x}}, {'_id': False,'_cls': False,'driver_id':False}))
    route_results2=list(mongo.db.route.find({ "_id":{"$in":x}},{'_id': True,'routeName': True,'_id': True,'departureCity': True,'departureCode': True,'destinationCity': True,'desinationCode': True,'departureHour':True, 'departureMin': True,'travelTimeHour': True,'travelTimeMin': True}))
    print(route_results2)
    #data_indirect=(json2html.convert(indir_results.to_json()))
    #routes_indirect=[]

    
    if not route_exists_direct_day:
        return render_template('404.html')
    else:
        return render_template('route_exist_day.html', direct_data=route_results1, indirect_data=route_results2 )


