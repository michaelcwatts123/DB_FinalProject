from flask import Flask
from .extensions import mongo
from .routes import main
import os
from flask_pymongo import PyMongo


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = 'mongodb+srv://admin:FyJKue16fzF5et8v@cluster0.bbd6r.mongodb.net/mydb?retryWrites=true&w=majority'
    #app.config["MONGO_URI"] = 'mongodb+srv://project_user:7330@busnetwork.nwlcz.mongodb.net/BusNetwork?retryWrites=true&w=majority'
    app.config["FILE_UPLOADS"] = '/static/file/uploads'
    mongo = PyMongo(app)
    mongo.init_app(app)

    app.register_blueprint(main)
    return app