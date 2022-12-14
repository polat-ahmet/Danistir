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

    def addToSession(self):
        with app.app_context():
            db.session.add(self)

    def merge(self):
        with app.app_context():
            db.session.merge(self)

    def mergeAndCommit(self):
        with app.app_context():
            db.session.merge(self)
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
    def find_by_id(cls, id):
        with app.app_context():
            result = db.session.execute(db.select(cls).filter_by(consultantAreaId=id)).scalar()
            # result = db.session.query(cls).filter_by(name=name).first()
            # result = cls.query.filter_by(name=name).first()
        return result

    @classmethod
    def find_by_name(cls, name):
        with app.app_context():
            result = db.session.execute(db.select(cls).filter_by(name=name)).scalar()
            # result = db.session.query(cls).filter_by(name=name).first()
            # result = cls.query.filter_by(name=name).first()
        return result

class ConsultantSubArea(db.Model):
    consultantSubAreaId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    areaId = db.Column(db.Integer, db.ForeignKey('consultant_area.consultantAreaId'))

    def commit(self):
        with app.app_context():
            db.session.commit()

    def merge(self):
        with app.app_context():
            db.session.merge(self)

    def mergeAndCommit(self):
        with app.app_context():
            db.session.merge(self)
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
    def getAll(cls):
        with app.app_context():
            result = db.session.query(cls).all()
        return result

    @classmethod
    def find_by_name(cls, name):
        with app.app_context():
            result = db.session.query(cls).options(db.orm.subqueryload(cls.area)).filter_by(name=name).first()
            # result = db.session.execute(db.select(cls).filter_by(name=name)).scalar()
            # result = db.session.query(cls).filter_by(name=name).first()
            # result = cls.query.filter_by(name=name).first()
        return result
    
    @classmethod
    def find_by_id(cls, _id):
        with app.app_context():
            result = db.session.query(cls).filter_by(consultantSubAreaId=_id).first()
        return result




consultantProvideSubArea = db.Table('consultant_provide_sub_area',
    db.Column('consultantInfoId', db.Integer, db.ForeignKey('consultant_info.consultantInfoId'), primary_key=True),
    db.Column('ConsultantSubAreaId', db.Integer, db.ForeignKey('consultant_sub_area.consultantSubAreaId'), primary_key=True)
)

class Appointment(db.Model):
    appointmentId = db.Column(db.Integer, primary_key=True)
    consultantUserId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    clientUserId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    appointmentDate = db.Column(db.DateTime, nullable=False)
    appointmentTimeInMin = db.Column(db.Integer, db.CheckConstraint('appointmentTimeInMin >= 0'), nullable=False, default=60)
    appointmentToken = db.Column(db.Text, nullable=False)

    consultant = db.relationship("User", backref="consultantAppointment", foreign_keys=[consultantUserId])
    client = db.relationship("User", backref="clientAppointment", foreign_keys=[clientUserId])

    def commit(self):
        with app.app_context():
            db.session.commit()

    def addToSession(self):
        with app.app_context():
            db.session.add(self)

    def merge(self):
        with app.app_context():
            db.session.merge(self)

    def mergeAndCommit(self):
        with app.app_context():
            db.session.merge(self)
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
    def find_consultant_appointments_by_id(cls, id):
        with app.app_context():
            result = db.session.query(cls).filter_by(consultantUserId=id).all()
        return result
    
    @classmethod
    def find_client_appointments_by_id(cls, id):
        with app.app_context():
            result = db.session.query(cls).filter_by(clientUserId=id).all()
        return result
    
    @classmethod
    def find_by_id(cls, id):
        with app.app_context():
            result = db.session.query(cls).filter_by(appointmentId=id).first()
        return result


class ConsultantWorkingTimes(db.Model):
    consultantWorkingTimesId = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, db.CheckConstraint('day >= 0 AND day < 7'))
    startHour = db.Column(db.Integer)
    endHour = db.Column(db.Integer)
    startMin = db.Column(db.Integer)
    endMin = db.Column(db.Integer)

    consultantInfoId = db.Column(db.Integer, db.ForeignKey('consultant_info.consultantInfoId'), nullable=False)


    def commit(self):
        with app.app_context():
            db.session.commit()

    def addToSession(self):
        with app.app_context():
            db.session.add(self)

    def merge(self):
        with app.app_context():
            db.session.merge(self)

    def mergeAndCommit(self):
        with app.app_context():
            db.session.merge(self)
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
    def resetConsultantWorkingTimes(cls, id):
        with app.app_context():
            db.session.query(cls).filter_by(consultantInfoId=id).delete()
            db.session.commit()

    @classmethod
    def find_by_id(cls, id):
        with app.app_context():
            result = db.session.execute(db.select(cls).filter_by(consultantWorkingTimesId=id)).scalar()
            # result = db.session.query(cls).filter_by(name=name).first()
            # result = cls.query.filter_by(name=name).first()
        return result

    @classmethod
    def find_by_consultant_id(cls, id):
        with app.app_context():
            result = db.session.query(cls).filter_by(consultantInfoId=id).all()
            # result = db.session.execute(db.select(cls).filter_by(consultantInfoId=id)).scalars()
            # result = db.session.query(cls).filter_by(name=name).first()
            # result = cls.query.filter_by(name=name).first()
        return result

class ConsultantInfo(db.Model):
    consultantInfoId = db.Column(db.Integer, primary_key=True)
    biography = db.Column(db.Text)
    average_rating = db.Column(db.Float, default=0)
    total_review = db.Column(db.Integer, default=0)

    consultant_id = db.Column(db.Integer, db.ForeignKey('user.userId'), unique=True)
    provideSubAreas = db.relationship('ConsultantSubArea', secondary=consultantProvideSubArea, lazy='subquery',
        backref=db.backref('consultants', lazy='subquery'))
    
    workingTimes = db.relationship("ConsultantWorkingTimes", backref='consultantInfo', lazy='subquery')

    @classmethod
    def find_by_id(cls, _id):
        with app.app_context():
            result = db.session.query(cls).filter_by(consultantInfoId=_id).first()
        return result
    
    @classmethod
    def find_by_id_with_areas(cls, _id):
        with app.app_context():
            result = db.session.query(cls).options(db.orm.subqueryload(cls.provideSubAreas)).filter_by(consultantInfoId=_id).first()
        return result
    
    @classmethod
    def find_by_id_with_areas_and_working_times(cls, _id):
        with app.app_context():
            result = db.session.query(cls).options(db.orm.subqueryload(cls.provideSubAreas), db.orm.subqueryload(cls.workingTimes)).filter_by(consultantInfoId=_id).first()
        return result
    
    def resetProvideSubAreas(self):
        with app.app_context():
            self.provideSubAreas = []

    def appendProvideSubAreas(self, subArea):
        with app.app_context():
            self.provideSubAreas.append(subArea)

    def mergeAndCommit(self):
        with app.app_context():
            db.session.merge(self)
            db.session.commit()

    def commit(self):
        with app.app_context():
            db.session.commit()
    
    def addToSession(self):
        with app.app_context():
            db.session.add(self)

    def merge(self):
        with app.app_context():
            db.session.merge(self)

    def mergeAndCommit(self):
        with app.app_context():
            db.session.merge(self)
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
        self.commit()
    
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

    def merge(self):
        with app.app_context():
            db.session.merge(self)

    def mergeAndCommit(self):
        with app.app_context():
            db.session.merge(self)
            db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        with app.app_context():
            # result = db.session.query(cls).filter_by(email=email).first()
            result = db.session.execute(db.select(cls).filter_by(email=email)).scalar()
            # result = cls.query.filter_by(email=email).first()
        return result
    
    @classmethod
    def getConsultants(cls):
        with app.app_context():
            result = db.session.query(cls).filter_by(is_consultant=True).all()
        return result

    @classmethod
    def find_by_id(cls, _id):
        with app.app_context():
            result = db.session.query(cls).filter_by(userId=_id).first()
            # result = cls.query.filter_by(userId=_id).first()
        return result


    def setFirstName(self, first_name):
        with app.app_context():
            self.first_name = first_name
            db.session.commit()

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
        # db.drop_all()
        # ConsultantWorkingTimes.__table__.drop(db.engine)
        db.create_all()
        print("Done!")