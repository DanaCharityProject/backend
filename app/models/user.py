"""
User
====================================
The User module
"""

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from ..validators import is_valid_username
from jwt import InvalidTokenError, ExpiredSignatureError
from email.message import EmailMessage

from .. import db

import jwt
import datetime

USER_ROLE_USER = "user"
USER_ROLE_ADMIN = "admin"


class User(db.Model):
    """The User Class"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(256), unique=True, nullable=False, index=True)
    role = db.Column(db.String(64), default=USER_ROLE_USER, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Checks hashed user password against plaintext password

        :param password: plaintext password
        :returns: True if password hashes match, false otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        """Generates a JSON Web Token which can be used to authenticate user requests.

        :param expiration: How long, in seconds, is the token valid.
        :returns: json web token encoded string
        """
        token = {
            'user_id': self.user_id,
            'role': self.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiration)
        }

        return jwt.encode(token, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

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

        # TODO: Figure out sending the email
        email_hash = jwt.encode(
            {'email' : user.email.lower()},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

        return user, email_hash

    def edit_user(self, username):
        try:
            if not is_valid_username(username):
                raise InvalidUserInfo("User information is invalid.")

            db.session.commit()
        except InvalidUserInfo:
            raise

    @classmethod
    def activate_user(cls, email_hash):
        print(email_hash)
        email_dict = jwt.decode(email_hash, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = cls.get_user_by_email(email_dict['email'])
        if user is not None:
            user.active = True
            db.session.commit()
            return True

    def change_password(self, password):
        self.password = password

        db.session.commit()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role,
            "active": self.active
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
