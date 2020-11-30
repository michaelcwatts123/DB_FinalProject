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
import pprint
from datetime import datetime


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
                                Assignment.save(z)

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


def routeCheck(start, end, day):
    route_exist_day_dept = start
    route_exist_day_dest = end
    route_exist_day_day = day
    
#    print(route_exist_day_dept+' '+route_exist_day_dest+' '+route_exist_day_day)
    route_exists_results= Route.objects.filter((Q(departureCity=route_exist_day_dept)) | (Q(destinationCity=route_exist_day_dest)) )
#    print(jsonify(route_exists_results.to_json()))
    routes=[]
    for rt in route_exists_results:
        routes.append(rt.routeNumber)
#    print(routes)
    route_exists_day = Assignment.objects.filter(routeNumber__in=routes, weekDay=route_exist_day_day)
    if not route_exists_day:
        return None
    else:
        return route_exists_day

@main.route('/validate', methods=['GET'])
def validate():
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
                                        pprint.pprint(sTime)
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
#                                pprint.pprint(vals[j][0]['destinationCity'] + ' ' + nextTrips[-1][0]['departureCity'] + ' ' + nextTrips[0][1][0] + ' ' + nextTrips[0][1][-1])
                                assignmentsToRemove.append((i, nextTrips[-1][0]['_id'], nextTrips[0][1][-1]))
                            else:
                                break
                        else:
                            break
    
#        pprint.pprint(vals)
    pprint.pprint(assignmentsToRemove)
#    if(len(assignmentsToRemove) > 0):
#        for i in assignmentsToRemove:
#            Assignment.objects.filter(driver_id=i[0],routeNumber=i[1], weekDay=i[2]).delete()
#        validate()
    return render_template('base.html', data=assignmentsToRemove)
    
