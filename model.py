from app import db, ma
from marshmallow import fields



class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime)


    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_consultant = db.Column(db.Boolean, default=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def hash_password(self, password):
        self.password = password
        # self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        if self.password == password:
            return True
        else:
            return False
        # return pwd_context.verify(password, self.password)

    def commit(self):
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(userId=_id).first()



class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ("password","created_date")




if __name__ == "__main__":
    print("Creating database tables...")
    # db.drop_all()
    db.create_all()
    print("Done!")