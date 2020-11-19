from flask import Blueprint, render_template, redirect, url_for, request
from flask import Flask
import os

app = Flask(__name__)
app.config["FILE_UPLOADS"] = './BusNetwork/static/uploads'

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route("/upload-docs", methods=["GET", "POST"])
def upload_docs():
    
    if request.method == "POST":

        if request.files:

            file = request.files.getlist("files")

            for fil in file:
                if fil.name == "":
                    print("No filename")
                    return render_template("index.html")
                fil.save(os.path.join(app.config["FILE_UPLOADS"], fil.filename))
                print(fil.filename)
            return redirect(request.url)
    return render_template("index.html")

@main.route('/driver_lookup', methods=['POST'])
def driver_lookup():
    driver_fn = request.form.get('driver_fn')
    driver_ln = request.form.get('driver_ln')
    driver_fn = driver_fn+ ' '+driver_ln
    print(driver_fn)
    #driver_results= Driver.objects(driver).get_or_404()
    return redirect(url_for('main.index'))


@main.route('/city_lookup', methods=['POST'])
def city_lookup():
    city_dest = request.form.get('city_lookup')
    print(city_dest)
    return redirect(url_for('main.index'))


@main.route('/route_lookup', methods=['POST'])
def route_lookup():
    route = request.form.get('route_lookup')
    print(route)
    return redirect(url_for('main.index'))


@main.route('/route_exist_lookup', methods=['POST'])
def route_exist_lookup():
    route_exist_dept = request.form.get('route_exist_dept')
    route_exist_dest = request.form.get('route_exist_dest')
    print(route_exist_dept+' '+route_exist_dest)
    return redirect(url_for('main.index'))

@main.route('/route_exist_day_lookup', methods=['POST'])
def route_exist_day_lookup():
    route_exist_day_dept = request.form.get('route_exist_day_dept')
    route_exist_day_dest = request.form.get('route_exist_day_dest')
    route_exist_day_day = request.form.get('route_exist_day_day')
    print(route_exist_day_dept+' '+route_exist_day_dest+' '+route_exist_day_day)
    return redirect(url_for('main.index'))


