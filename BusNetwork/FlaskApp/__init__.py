from flask import Flask
from .extensions import mongo
from .main.routes import main

def create_app():
    app = Flask(__name__)
    app.config['MONGO_URI'] ='mongodb+srv://admin:FyJKue16fzF5et8v@cluster0.bbd6r.mongodb.net/mydb?retryWrites=true&w=majority'
    app.config["FILE_UPLOADS"] = '/static/file/uploads'

    mongo.init_app(app)

    app.register_blueprint(main)
    return app