from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta

api = Api()
jwt = JWTManager()
ma = Marshmallow()


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Danistir secret key' 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

db = SQLAlchemy(app)

## ROUTES ###
def addRoutes():
    from controller import UserRegister, Login, Profile, PasswordChange, ConsultantInfoController
    api.add_resource(UserRegister, "/register") #POST ,parameters: email, password ; return: message
    api.add_resource(Login, "/login") #POST ,parameters: email, password ; return: message, access_token (if success)
    api.add_resource(Profile, "/profile") #token required (must be logged-in) | GET, ; return: email, repos[]
    api.add_resource(PasswordChange, "/password") #token required (must be logged-in) | PATCH (change password logged-in user's), paramaters: old_password, new_password ; return: message
    api.add_resource(ConsultantInfoController, "/consultant") #


# if __name__ == '__main__':
addRoutes()

api.init_app(app)
jwt.init_app(app)
ma.init_app(app)

CORS(app)

    
    # app.run(debug=True)
