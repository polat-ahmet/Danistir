from flask_restful import Resource, reqparse
from flask import jsonify
from model import *
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json
from serializer import *
import datetime



class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str, help="Email is required", required=True)
    parser.add_argument('password', type=str, help="Password is required", required=True)
    parser.add_argument('isConsultant', type=bool, help="isConsultant is required", required=True)
    parser.add_argument('name', type=str, help="name is required", required=True)
    parser.add_argument('surname', type=str, help="surname is required", required=True)

    def post(self):
        data = UserRegister.parser.parse_args()
        if User.find_by_email(data['email']):
            return {'message': 'Email has already been taken'}, 400
        user = User(email=data['email'], password=data['password'], is_consultant=data['isConsultant'], first_name=data['name'], last_name=data['surname'])
        user.hash_password(data['password'])
        if user.is_consultant:
            consultant_info = ConsultantInfo(consultant=user)
            consultant_info.addToSession()
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
    parser.add_argument('name')
    parser.add_argument('surname')
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
    def post(self):
        data = Profile.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)
        if data["name"]:
            user.setFirstName(data["name"])
        if data["surname"]:
            user.setLastName(data["surname"])
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
            return {'message': 'Currently Password is wrong'}, 400
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

    @jwt_required()
    def get(self):
        data = ConsultantAreaAddController.parser.parse_args()
        consultantArea = ConsultantArea.find_by_name(data['name'])
        if consultantArea:
            print(consultantArea.subAreas)
            consultantSubAreaSchema = ConsultantAreaSchema()
            output = consultantSubAreaSchema.dump(consultantArea)
            return jsonify(output)
        return {'message': 'Consultant Area Not Found'}, 404

#consultant Subarea ekleme sadece admin ekleyebilir
class ConsultantSubAreaAddController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, help="Consultant SubArea Name required", required=True)
    parser.add_argument('area_name', type=str, help="Consultant Area Name required", required=True)
    getParser = reqparse.RequestParser()
    getParser.add_argument('name', type=str, help="Consultant SubArea Name required", required=True)

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
                ##
                print("-------")
                print(consultantSubArea.area)
                print(consultantArea.subAreas)
                # consultantArea.merge()
                # consultantSubArea.merge()
                # consultantSubArea.area.merge()
                consultantSubArea.save_to_db()
                # consultantArea.save_to_db()
                return {'message':  'Consultant SubArea has been added successfully'}, 201
            return {'message': 'Consultant SubArea Not Found'}, 404
        return {'message': 'Only Admin can add'}, 401

    @jwt_required()
    def get(self):
        data = ConsultantSubAreaAddController.parser.parse_args()
        consultantSubArea = ConsultantSubArea.find_by_name(data['name'])
        # print("----++++---")
        # print(consultantSubArea)
        if consultantSubArea:
            # print("-------")
            # print(consultantSubArea.name)
            # print(consultantSubArea.areaId)
            # print(consultantSubArea.area.name)
            consultantSubAreaSchema = ConsultantSubAreaSchema()
            output = consultantSubAreaSchema.dump(consultantSubArea)
            consultantArea = ConsultantArea.find_by_id(consultantSubArea.areaId)
            # print(consultantArea.name)
            # return {'message': 'debug'}, 400
            # return jsonify(output)
            return {'message': output}, 200
        return {'message': 'Consultant SubArea Not Found'}, 404

class ConsultantSubAreasController(Resource):

    def get(self):
        consultantSubAreas = ConsultantSubArea.getAll()

        if consultantSubAreas:
            consultantSubAreaSchema = ConsultantSubAreaSchema(many=True)
            output = consultantSubAreaSchema.dump(consultantSubAreas)

            return {'subAres': output}, 200
        return {'message': 'Consultant SubArea Not Found'}, 404

#consultant çalıştığı saatleri ayarlama
class ConsultantWorkTimeController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('time', type=dict, help="required", required=True, action='append')

    @jwt_required()
    def post(self):
        data = ConsultantWorkTimeController.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        if user.is_consultant:
            times = data["time"]
            ConsultantWorkingTimes.resetConsultantWorkingTimes(user.consultant_info.consultantInfoId)        
            for element in times:
                consultantWorkingTimesSchema = ConsultantWorkingTimesSchema()
                output = consultantWorkingTimesSchema.load(element)

                consultantWorking = ConsultantWorkingTimes(**output, consultantInfo=user.consultant_info)
                consultantWorking.save_to_db()
            
            return {'message': 'Consultant Working Times Successfully Created'}, 201

        return {'message': 'You are not consultant'}, 401

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        if user.is_consultant:
            workingTimes = ConsultantWorkingTimes.find_by_consultant_id(user.consultant_info.consultantInfoId)
            consultantWorkingTimesSchema = ConsultantWorkingTimesSchema(many=True)
            output = consultantWorkingTimesSchema.dump(workingTimes)
            return {'time': output, 'consultantInfoId':user.consultant_info.consultantInfoId, 'userId':user.userId}, 200

        return {'message': 'You are not consultant'}, 401


class ConsultantServiceSettingsController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('time', type=dict, help="required", action='append')
    parser.add_argument('subAreas', type=dict, help="required", action='append')

    @jwt_required()
    def post(self):
        data = ConsultantServiceSettingsController.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        if user.is_consultant:
            if data["time"]:
                times = data["time"]
                ConsultantWorkingTimes.resetConsultantWorkingTimes(user.consultant_info.consultantInfoId)        
                for element in times:
                    consultantWorkingTimesSchema = ConsultantWorkingTimesSchema()
                    output = consultantWorkingTimesSchema.load(element)

                    consultantWorking = ConsultantWorkingTimes(**output, consultantInfo=user.consultant_info)
                    consultantWorking.save_to_db()
            if data["subAreas"]:
                subAreas = data["subAreas"]
                user = User.find_by_email(current_user)
                consultantInfo = ConsultantInfo.find_by_id_with_areas(user.consultant_info.consultantInfoId)
                # print(consultantInfo.provideSubAreas)
                consultantInfo.resetProvideSubAreas()
                for element in subAreas:
                    subArea = ConsultantSubArea.find_by_name(element["name"])
                    if subArea:
                        consultantInfo.appendProvideSubAreas(subArea)
                consultantInfo.mergeAndCommit()
            return {'message': 'Consultant Service Settings Successfully Changed'}, 201
        return {'message': 'You are not consultant'}, 401

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        if user.is_consultant:
            consultantInfo = ConsultantInfo.find_by_id_with_areas_and_working_times(user.consultant_info.consultantInfoId)
            # print(consultantInfo.provideSubAreas)
            # print(consultantInfo.workingTimes)
            consultantWorkingTimesSchema = ConsultantWorkingTimesSchema(many=True)
            consultantSubAreaSchema = ConsultantSubAreaSchema(many=True)
            
            workingTimesOutput = consultantWorkingTimesSchema.dump(consultantInfo.workingTimes)
            subAreasOutput = consultantSubAreaSchema.dump(consultantInfo.provideSubAreas)
            
            return {'time': workingTimesOutput, 'subAreas':subAreasOutput, 'consultantInfoId':user.consultant_info.consultantInfoId, 'userId':user.userId}, 200

        return {'message': 'You are not consultant'}, 401

def getConsultantFreeTimes(id):
    user = User.find_by_id(id)
    workingTimes = ConsultantWorkingTimes.find_by_consultant_id(user.consultant_info.consultantInfoId)
    consultantWorkingTimesSchema = ConsultantWorkingTimesSchema(many=True)
    workingTimesOutput = consultantWorkingTimesSchema.dump(workingTimes)

    appointments = Appointment.find_consultant_appointments_by_id(user.userId)
    appointmentsSchema = AppointmentSchema(many=True)
    appointmentsOutput = appointmentsSchema.dump(appointments)

    print(workingTimesOutput)
    print("--appointments--", appointmentsOutput)
    timeDictList = []

    j = 0
    while workingTimesOutput and j<len(workingTimesOutput):
            # for element in workingTimesOutput:
        element = workingTimesOutput[j]
        today = datetime.datetime.now()
        dateTime = today + datetime.timedelta( (element["day"]-today.weekday()) % 7 )

        startDateTime = dateTime.replace(hour=element["startHour"], minute=element["startMin"], second=0, microsecond=0)
        endDateTime = dateTime.replace(hour=element["endHour"], minute=element["endMin"], second=0, microsecond=0)    
              
        flag = False
        for i in appointmentsOutput:
            appointmentDate = datetime.datetime.strptime(i["appointmentDate"],'%Y-%m-%dT%H:%M:%S')
            if appointmentDate >= startDateTime and appointmentDate < endDateTime:
                print("----", element)
                print("---appointmentDate--", appointmentDate)
                if (appointmentDate.hour > startDateTime.hour and appointmentDate.hour+1 < endDateTime.hour):
                    tempElement = element.copy()
                    tempElement["endHour"] = appointmentDate.hour
                    print("---temp11----", tempElement)
                    workingTimesOutput.append(tempElement)

                    tempElement = element
                    tempElement["startHour"] = appointmentDate.hour+1
                    print("---temp22----", tempElement)
                    workingTimesOutput.append(tempElement)                           
                elif (appointmentDate.hour > startDateTime.hour and appointmentDate.hour+1 == endDateTime.hour):
                    tempElement = element.copy()
                    tempElement["endHour"] = appointmentDate.hour
                    print("---temp33----", tempElement)
                    workingTimesOutput.append(tempElement)
                elif (appointmentDate.hour == startDateTime.hour and appointmentDate.hour+1 < endDateTime.hour):
                    tempElement = element
                    tempElement["startHour"] = appointmentDate.hour+1
                    print("---temp44----", tempElement)
                    workingTimesOutput.append(tempElement)                            
                        # workingTimesOutput.remove(element)
                flag = True
        if not flag:
            startDateString = startDateTime.strftime('%a %b %d %Y %H:%M:%S')
            endDateString = endDateTime.strftime('%a %b %d %Y %H:%M:%S')

            startDateString +=' GMT+0300 (GMT+03:00)'
            endDateString +=' GMT+0300 (GMT+03:00)'
            timeDict = {'start':startDateString, 'end':endDateString}
            timeDictList.append(timeDict)
        j+=1
    print("--",timeDictList)
    print("-+-",workingTimesOutput)

    return timeDictList

class ConsultantFreeTimeController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('consultantId', type=int, help="ConsultantId required", required=True)

    def get(self):
        data = ConsultantFreeTimeController.parser.parse_args()
        user = User.find_by_id(data["consultantId"])
        if user.is_consultant:
            result = getConsultantFreeTimes(data["consultantId"])
            return {'freeTimes':result}, 200

        return {'message': 'User is not consultant'}, 401

#appointment alma 
class TakeAppointmentController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userId', type=int, help="UserId required", required=True)
    parser.add_argument('consultantId', type=int, help="ConsultantId required", required=True)
    parser.add_argument('appointmentDate', type=lambda x: datetime.datetime.strptime(x,'%a %b %d %Y %H:%M:%S'), help="appointmentDate required", required=True)
    getParser = reqparse.RequestParser()
    getParser.add_argument('consultantId', type=int, help="consultantId required", required=True)

    @jwt_required()
    def post(self):
        data = TakeAppointmentController.parser.parse_args()
        current_user = get_jwt_identity()
        user = User.find_by_email(current_user)

        if user:
            #generate agora token
            from agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
            import time      
            appID = "651567b3ecc3473e806ec776ae53781a"
            appCertificate = "4e6c5235d5ee47a2941589c3ea7c945b"
            channelName = "danistirchannel"
            uid = 0
            expireTimeInSeconds = 36000000
            currentTimestamp = int(time.time())
            privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

            appointmentToken = RtcTokenBuilder.buildTokenWithUid(appID, appCertificate, channelName, uid, Role_Attendee, privilegeExpiredTs)
            print("Token with int uid: {}".format(appointmentToken))
            ##
            
            print(data["appointmentDate"])
            appointmentDate = data["appointmentDate"]
            client = User.find_by_id(data["userId"])
            consultant = User.find_by_id(data["consultantId"])
            if client and consultant:
                appointment = Appointment(consultantUserId=consultant.userId, clientUserId=client.userId, appointmentDate=appointmentDate, appointmentToken=appointmentToken)
                appointment.save_to_db()
                return {'message': 'Appointment successfully take'}, 201
            return {'message': 'Client or Consultant Not Found'}, 404

        return {'message': 'Error'}, 400

    

class ConsultantAppointmentsController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('consultantId', type=int, help="ConsultantId required", required=True)

    def get(self):
        data = ConsultantAppointmentsController.parser.parse_args()
        user = User.find_by_id(data["consultantId"])
        if user.is_consultant:
            appointments = Appointment.find_consultant_appointments_by_id(user.userId)
            appointmentsSchema = AppointmentSchema(many=True)
            output = appointmentsSchema.dump(appointments)
            return jsonify(output)
                # return {'message': 'Consultant\'s appointments'}, 200
        return {'message': 'User is not consultant'}, 401

class ClientAppointmentsController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userId', type=int, help="UserId required", required=True)

    def get(self):
        data = ClientAppointmentsController.parser.parse_args()
        user = User.find_by_id(data["userId"])
        if user:
            appointments = Appointment.find_client_appointments_by_id(user.userId)
            appointmentsSchema = AppointmentSchema(many=True)
            output = appointmentsSchema.dump(appointments)
            return jsonify(output)
        return {'message': 'User is not found'}, 401

#TODO keyworda gore search yap
class SearchController(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('searchWord', type=int, help="searchWord required")

    def get(self):
        consultants = User.getConsultants()
        if consultants:
            user_schema = UserSchema(many=True)
            output = user_schema.dump(consultants)
            # print(output)
            for i in output:
                print(i)
                result = getConsultantFreeTimes(i["userId"])
                i["consultant_info"]["freeTimes"] = result
            return jsonify(output)
        return {'message': 'Consultant is not found'}, 404