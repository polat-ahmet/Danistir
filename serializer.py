from model import *
from app import ma
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import Schema, fields


class ConsultantAreaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsultantArea
        # include_relationships = True
        load_instance = True
      
    # subAreas = Nested(ConsultantSubAreaSchema, many=True) 


class ConsultantSubAreaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsultantSubArea
        # include_relationships = True
        load_instance = True
      
    # area = Nested(ConsultantAreaSchema)

class AppointmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Appointment
        load_instance = True
        # exclude = ("appointmentToken",)

class ConsultantInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsultantInfo
        # include_relationships = True
        load_instance = True
        include_fk = True
      
    provideSubAreas = Nested(ConsultantSubAreaSchema, many=True)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ("password","created_date")

    consultant_info = Nested(ConsultantInfoSchema)


class ConsultantWorkingTimesSchema(Schema):
    day = fields.Int()
    startHour = fields.Int()
    startMin = fields.Int()
    endHour = fields.Int()
    endMin = fields.Int()
    # class Meta:
    #     fields = ('day', 'startHour', 'startMin', 'endHour', 'endMin')