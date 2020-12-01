from flask import Flask
from .extensions import mongo
from .main.routes import main
import os
from mongoengine import connect


def create_app(config_object='BusNetwork.settings'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    connect('BusNetwork', host='mongodb+srv://admin:FyJKue16fzF5et8v@cluster0.bbd6r.mongodb.net/BusNetwork?retryWrites=true&w=majority')
    app.config["MONGO_URI"] = 'mongodb+srv://admin:FyJKue16fzF5et8v@cluster0.bbd6r.mongodb.net/mydb?retryWrites=true&w=majority'
    #app.config["MONGO_URI"] = 'mongodb+srv://project_user:7330@busnetwork.nwlcz.mongodb.net/BusNetwork?retryWrites=true&w=majority'
    app.config["FILE_UPLOADS"] = '/static/file/uploads'
   

    mongo.init_app(app)

    app.register_blueprint(main)
    return app