from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask import Flask
import os, json, csv#, #models
from csv import reader
from .extensions import mongo
from flask_pymongo import PyMongo
from .models import Driver, Assignment, Route
from flask_mongoengine import MongoEngine
from mongoengine.queryset.visitor import Q


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
    #driver_fulln = driver_fn+ ' '+driver_ln
    print(driver_fn)
    driver_results= Driver.objects(firstName=driver_fn)
    if not driver_results:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(driver_results.to_json())
    #return jsonify(driver_fn)


@main.route('/city_lookup', methods=['POST'])
def city_lookup():
    city_dest = request.form.get('city_lookup')
    city_results= Route.objects(departureCity=city_dest)
    if not city_results:
        return jsonify({'error': 'data not found'})
    else:
        return (city_results.to_json())


@main.route('/route_lookup', methods=['POST'])
def route_lookup():
    route_exist = request.form.get('route_lookup')
    route_results= Assignment.objects(routeNumber=route_exist)
    if not route_results:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(route_results.to_json())


@main.route('/route_exist_lookup', methods=['POST'])
def route_exist_lookup():
    route_exist_dept = request.form.get('route_exist_dept')
    route_exist_dest = request.form.get('route_exist_dest')
    route_exists_results= Route.objects(departureCity=route_exist_dept, destinationCity=route_exist_dest )
    if not route_exists_results:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(route_exists_results.to_json())

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
    if not route_exists_day:
        return jsonify({'error': 'data not found'})
    else:
        return jsonify(route_exists_day.to_json())#jsonify(route_exists_day.to_json())


