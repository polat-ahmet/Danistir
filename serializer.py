from model import *
from app import ma
from marshmallow_sqlalchemy.fields import Nested

class ConsultantInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsultantInfo
        include_relationships = True
        load_instance = True


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ("password","created_date")

    consultant_info = Nested(ConsultantInfoSchema)