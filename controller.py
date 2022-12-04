from flask_restful import Resource, reqparse
from flask import jsonify
from model import *
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json
from serializer import *



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
    
        user.mergeAndCommit()
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
        user.mergeAndCommit()
        return {'message':  'Password changed successfully'}, 200        

class ConsultantInfoController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('biography')
    parser.add_argument('average_rating')
    parser.add_argument('total_review')

    # TODO response dön
    @jwt_required()
    def post(self):
        data = ConsultantInfoController.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        #eger user danışmansa
        if user.is_consultant:
            #userın consultant infosu daha önce oluşturulmadıysa yeniden oluştur
            if not user.consultant_info:
                consultant_info = ConsultantInfo(**data,consultant=user)
                consultant_info.save_to_db()
                
            #user consultant info varsa, editleme
            else:
                if data["biography"]:
                    user.consultant_info.setBiography(data["biography"])
                if data["average_rating"]:
                    user.consultant_info.setAverageRating(data["average_rating"])
                if data["total_review"]:
                    user.consultant_info.setTotalReview(data["total_review"])
                user.mergeAndCommit()
            return {'message': 'Consultant info succesfully changed'}, 200
        return {'message': 'You are not consultant'}, 401

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        if user.is_consultant:
            consultant_info_schema = ConsultantInfoSchema()
            output = consultant_info_schema.dump(user.consultant_info)
            return jsonify(output)
        return {'message': 'You are not consultant'}, 401


#consultant area ekleme sadece admin ekleyebilir
class ConsultantAreaAddController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, help="Consultant Area Name required", required=True)

    @jwt_required()
    def post(self):
        data = ConsultantAreaAddController.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        #eger user adminse
        if user.is_admin:
            if ConsultantArea.find_by_name(data['name']):
                return {'message': 'Consultant Area has already been added'}, 400
            consultantArea = ConsultantArea(name=data['name'])
            consultantArea.save_to_db()
            return {'message':  'Consultant Area has been added successfully'}, 201
        return {'message': 'Only Admin can add'}, 401


#consultant Subarea ekleme sadece admin ekleyebilir
class ConsultantSubAreaAddController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, help="Consultant SubArea Name required", required=True)
    parser.add_argument('area_name', type=str, help="Consultant Area Name required", required=True)

    @jwt_required()
    def post(self):
        data = ConsultantSubAreaAddController.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        #eger user adminse
        if user.is_admin:
            if ConsultantSubArea.find_by_name(data['name']):
                return {'message': 'Consultant SubArea has already been added'}, 400
            consultantArea = ConsultantArea.find_by_name(data['area_name'])
            if consultantArea:
                consultantSubArea = ConsultantSubArea(name=data['name'], area=consultantArea)
                consultantSubArea.save_to_db()
                return {'message':  'Consultant SubArea has been added successfully'}, 201
            return {'message': 'Consultant Area Not Found'}, 404
        return {'message': 'Only Admin can add'}, 401

