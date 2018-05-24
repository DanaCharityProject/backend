from flask import current_app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from werkzeug.security import check_password_hash, generate_password_hash
from ..validators import is_valid_username

from .. import db

USER_ROLE_USER = "user"
USER_ROLE_ADMIN = "admin"

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    role = db.Column(db.String(64), default=USER_ROLE_USER, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # email = db.Column(db.String(64), unique=True,
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

        return s.dumps({
            "user_id": self.user_id,
            "role": self.role
        })

    @staticmethod
    def verify_auth_token(token):
        return UserManager.get_user_by_token(token)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }

    @staticmethod
    def get_user_by_username(username):
        return UserManager.get_user_by_username(username)

            return cls.query.get(data["user_id"])


class UserManager():

    @staticmethod
    def add_user(user):
        if User.get_user_by_username(user.username) is not None:
            return None

        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def edit_user(user_id, new_username):
        user = User.query.get(user_id)
        try:
            if not is_valid_username(new_username):
                raise InvalidUserInfo("User information is invalid.")
            user.username = new_username
        except InvalidUserInfo:
            raise

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class InvalidUserInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
