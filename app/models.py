from flask import current_app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from werkzeug.security import check_password_hash, generate_password_hash
from .validators import is_valid_username, is_valid_email, is_valid_phone_number, is_valid_community_resource_name

from . import db

class NoExistingUser(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidUserInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class NoExistingCommunityResource(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidCommunityResourceInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class UserManager():

    @staticmethod
    def edit_user(user_id, new_username):
        user = User.query.get(user_id)
        try:
            if user is None:
                raise NoExistingUser("Something went wrong!")
            if not is_valid_username(new_username):
                raise InvalidUserInfo("User information is invalid.")
            user.username = new_username
        except NoExistingUser:
            raise
        except InvalidUserInfo:
            raise


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True,
                         nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    #email = db.Column(db.String(64), unique=True,
    #                    nullable=True, index=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def add_user(user):
        if User.get_user_by_username(user.username) is not None:
            return None

        db.session.add(user)
        db.session.commit()
        return user


class CommunityResource(db.Model):
    __tablename__ = "community resources"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True,
                       nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    contact_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)

    @property
    def location(self):
        return self.lat, self.lon

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "verified": self.verified
        }

    @staticmethod
    def get_resource_by_number(number):
        return CommunityResource.query.filter_by(number=number).first()

    @staticmethod
    def add_community_resource(resource):
        if CommunityResource.get_resource_by_number(resource.number) is not None:
            return None

        db.session.add(resource)
        db.session.commit()
        return resource

 
class CommunityResourceManager():

    @staticmethod
    def edit_community_resource(number, new_name, new_lat, new_lon, new_contact_name, new_email, new_phone_number):
        resource = CommunityResource.get_resource_by_number(number)

        try:
            if resource is None:
                raise NoExistingCommunityResource("Community Resource does not exist.")
            if not is_valid_email(new_email):
                raise InvalidCommunityResourceInfo("New email address for Community Resource is invalid.")
            if not is_valid_phone_number(new_phone_number):
                raise InvalidCommunityResourceInfo("New phone number for Community Resource is invalid.")
            if not is_valid_community_resource_name(new_name):
                raise InvalidCommunityResourceInfo("New resource center name cannot be empty")
            resource.name = new_name
            resource.lat = new_lat
            resource.lon = new_lon
            resource.contact_name = new_contact_name
            resource.email = new_email
            resource.phone_number = new_phone_number
        except NoExistingCommunityResource:
            raise
        except InvalidCommunityResourceInfo:
            raise

