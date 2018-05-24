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

    @classmethod
    def verify_auth_token(cls, token):
        return cls.get_user_by_token(token)

    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username.lower()).first()

    @classmethod
    def get_user_by_token(cls, token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
            return cls.query.get(data["user_id"])
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        except:
            return None

    @classmethod
    def add_user(cls, user):
        if cls.get_user_by_username(user.username.lower()) is not None:
            return None

        db.session.add(user)
        db.session.commit()

        return user

    def edit_user(self, username):
        try:
            if not is_valid_username(username):
                raise InvalidUserInfo("User information is invalid.")

            self.username = username
            db.session.commit()
        except InvalidUserInfo:
            raise

    def change_password(self, password):
        self.password = password

        db.session.commit()

    def to_dict(self):
        return {
            "id": self.user_id,
            "username": self.username,
            "role": self.role
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class InvalidUserInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
