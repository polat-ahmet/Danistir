from flask_restful import Resource, reqparse
from flask import jsonify
from model import *
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json



class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str, help="Email is required", required=True)
    parser.add_argument('password', type=str, help="Password is required", required=True)

    def post(self):
        data = UserRegister.parser.parse_args()
        if User.find_by_email(data['email']):
            return {'message': 'Email has already been taken'}, 400
        user = User(**data)
        user.hash_password(data['password'])
        user.save_to_db()
        return {'message':  'User has been created successfully'}, 201


class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str, help="Email is required", required=True)
    parser.add_argument('password', type=str, help="Password is required", required=True)

    def post(self):
        data = Login.parser.parse_args()
        user = User.find_by_email(data['email'])
        if not user or not user.verify_password(data['password']):
            return {'message': 'Wrong Email or Password'}, 404
        access_token = create_access_token(identity=data['email'])
        return jsonify(message="Login Succeeded!", access_token=access_token)


class Profile(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('first_name')
    parser.add_argument('last_name')
    #parser.add_argument('email')
    parser.add_argument('address')
    parser.add_argument('image')

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)
        user_schema = UserSchema()
        output = user_schema.dump(user)
        return jsonify(output)


    @jwt_required()
    def put(self):
        data = Profile.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)
        if data["first_name"]:
            user.setFirstName(data["first_name"])
        if data["last_name"]:
            user.setLastName(data["last_name"])
        if data["address"]:
            user.setAddress(data["address"])
        if data["image"]:
            user.setImage(data["image"])
        #user.setEmail(data["email"])
    
        user.commit()
        return {'message':  'Profile changes updated'}, 200



#change password
class PasswordChange(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('old_password', type=str, help="Old Password is required", required=True)
    parser.add_argument('new_password', type=str, help="New Password is required", required=True)

    @jwt_required()
    def post(self):
        data = PasswordChange.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        if not user.verify_password(data['old_password']):
            return {'message': 'Currently Password is wrong'}, 404
        user.hash_password(data['new_password'])
        user.commit()
        return {'message':  'Password changed successfully'}, 200        


