from model import *
from app import ma
from marshmallow_sqlalchemy.fields import Nested


class ConsultantAreaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsultantArea
        include_relationships = True
        load_instance = True
      
    # subAreas = Nested(ConsultantSubAreaSchema, many=True) 


class ConsultantSubAreaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsultantSubArea
        # include_relationships = True
        load_instance = True
      
    # consultants = Nested(ConsultantSubAreaSchema, many=True)

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
        include_relationships = True
        load_instance = True
        exclude = ("password","created_date")

    consultant_info = Nested(ConsultantInfoSchema)