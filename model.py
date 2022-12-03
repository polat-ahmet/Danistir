from email.policy import default
from app import db, app
from marshmallow import fields
from marshmallow_sqlalchemy.fields import Nested


class ConsultantArea(db.Model):
    consultantAreaId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    subAreas = db.relationship('ConsultantSubArea', backref='area', lazy='subquery')

    def commit(self):
        with app.app_context():
            db.session.commit()

    def save_to_db(self):
        with app.app_context():
            db.session.add(self)
            db.session.commit()

    def delete_from_db(self):
        with app.app_context():
            db.session.delete(self)
            db.session.commit()

    @classmethod
    def find_by_name(cls, name):
        with app.app_context():
            result = cls.query.filter_by(name=name).first()
        return result

class ConsultantSubArea(db.Model):
    consultantSubAreaId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    areaId = db.Column(db.Integer, db.ForeignKey('consultant_area.consultantAreaId'),
        nullable=False)

    def commit(self):
        with app.app_context():
            db.session.commit()

    def save_to_db(self):
        with app.app_context():
            db.session.add(self)
            db.session.commit()

    def delete_from_db(self):
        with app.app_context():
            db.session.delete(self)
            db.session.commit()

    @classmethod
    def find_by_name(cls, name):
        with app.app_context():
            result = cls.query.filter_by(name=name).first()
        return result


consultantProvideSubArea = db.Table('consultant_provide_sub_area',
    db.Column('consultantInfoId', db.Integer, db.ForeignKey('consultant_info.consultantInfoId'), primary_key=True),
    db.Column('ConsultantSubAreaId', db.Integer, db.ForeignKey('consultant_sub_area.consultantSubAreaId'), primary_key=True)
)

class ConsultantInfo(db.Model):
    consultantInfoId = db.Column(db.Integer, primary_key=True)
    biography = db.Column(db.Text)
    average_rating = db.Column(db.Float, default=0)
    total_review = db.Column(db.Integer, default=0)

    consultant_id = db.Column(db.Integer, db.ForeignKey('user.userId'), unique=True)
    provideSubAreas = db.relationship('ConsultantSubArea', secondary=consultantProvideSubArea, lazy='subquery',
        backref=db.backref('consultants', lazy='subquery'))


    def commit(self):
        with app.app_context():
            db.session.commit()

    def save_to_db(self):
        with app.app_context():
            db.session.add(self)
            db.session.commit()

    def delete_from_db(self):
        with app.app_context():
            db.session.delete(self)
            db.session.commit()

    def setBiography(self, bio):
        self.biography = bio
    
    def setAverageRating(self, av_rat):
        self.average_rating = av_rat
    
    def setTotalReview(self, tot_rev):
        self.total_review = tot_rev



class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime)
    address = db.Column(db.Text)
    image = db.Column(db.Text)

    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_consultant = db.Column(db.Boolean, default=False)

    consultant_info = db.relationship("ConsultantInfo", backref='consultant', uselist=False, lazy='subquery')

    def save_to_db(self):
        with app.app_context():
            db.session.add(self)    
            db.session.commit()

    def delete_from_db(self):
        with app.app_context():
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
        with app.app_context():
            db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        with app.app_context():
            result = cls.query.filter_by(email=email).first()
        return result

    @classmethod
    def find_by_id(cls, _id):
        with app.app_context():
            result = cls.query.filter_by(userId=_id).first()
        return result


    def setFirstName(self, first_name):
        self.first_name = first_name

    def setLastName(self, last_name):
        self.last_name = last_name

    def setEmail(self, email):
        self.email = email

    def setAddress(self, address):
        self.address = address 

    def setImage(self, image):
        self.image = image 

    # TODO
    def setConsultantInfo(self, consultant_info):
        self.consultant_info =consultant_info


if __name__ == "__main__":
    print("********************* *-------------- Creating database tables...")
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Done!")