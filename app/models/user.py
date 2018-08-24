from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from ..validators import is_valid_username
from jwt import InvalidTokenError, ExpiredSignatureError

from .. import db

import jwt
import datetime


USER_ROLE_USER = "user"
USER_ROLE_ADMIN = "admin"


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(256), unique=True, nullable=False, index=True)
    role = db.Column(db.String(64), default=USER_ROLE_USER, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        token = {
            'user_id': self.user_id,
            'role': self.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiration)
        }

        return jwt.encode(token, current_app.config['SECRET_KEY'], algorithm='HS256')

    @classmethod
    def verify_auth_token(cls, token):
        return cls.get_user_by_token(token)

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email.lower()).first()

    @classmethod
    def get_user_by_token(cls, token):
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return cls.query.get(data["user_id"])
        except ExpiredSignatureError:
            return None    # valid token, but expired
        except InvalidTokenError:
            return None    # invalid token
        except:
            return None

    @classmethod
    def add_user(cls, user):
        if cls.get_user_by_email(user.email.lower()) is not None:
            return None

        db.session.add(user)
        db.session.commit()

        return user

    def edit_user(self, username):
        try:
            if not is_valid_username(username):
                raise InvalidUserInfo("User information is invalid.")

            db.session.commit()
        except InvalidUserInfo:
            raise

    def change_password(self, password):
        self.password = password

        db.session.commit()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role
        }
    
    @classmethod
    def from_dict(cls, data):
        # Ensure email address is case-insensitive
        email = data.get("email")
        if email is not None:
            data.update({"email": email.lower()})

        return cls(**data)


class InvalidUserInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
