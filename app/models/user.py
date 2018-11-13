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
    donation_code = db.Column(db.String(40), nullable=True)
    donation_code_is_stale = False
    balance = db.Column(db.Integer, default=0)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # @balance.setter
    # def balance(self, balance):
    #     self.balance = balance

    # @balance.getter
    # def balance(self, balance):
    #     return self.balance

    def reduce_balance(self, amount):
        self.balance = self.balance - amount

    def verify_password(self, password):
        """Checks hashed user password against plaintext password

        :param password: plaintext password
        :returns: True if password hashes match, false otherwise
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
        """Checks if token corresponds to correct user.
        
        :param cls: This User object 
        :param token: A hash string used to identify a user
        :returns: The user object if found or None
        """
        return cls.get_user_by_token(token)

    @classmethod
    def get_user_by_email(cls, email):
        """Get a user object by an identifying email.
        
        :param cls: This User object 
        :param email: An email used by a user
        :returns: The user object 
        """
        return cls.query.filter_by(email=email.lower()).first()

    @classmethod
    def get_user_by_token(cls, token):
        """Gets a user object given a token
        
        :param cls: This User object 
        :param token: A hash string used to identify a user
        :returns: The user object if found or None 
        """
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
        """Adds a user to the db.
        
        :param cls: This User object 
        :param user: A user object
        :returns: The user object and a hashed email 
        """
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
        """Change the username of a given user object.
        
        :param self: This User object 
        :param username: New username desired to be associated with this user object
        """
        try:
            if not is_valid_username(username):
                raise InvalidUserInfo("User information is invalid.")

            db.session.commit()
        except InvalidUserInfo:
            raise

    @classmethod
    def activate_user(cls, email_hash):
        """??
        
        :param cls: This User object 
        :param emailhash: A hash string of the email
        :returns: True if the activation was successful
        """
        print(email_hash)
        email_dict = jwt.decode(email_hash, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = cls.get_user_by_email(email_dict['email'])
        if user is not None:
            user.active = True
            db.session.commit()
            return True

    def change_password(self, password):
        """Update users password

        :param self: This user object
        :param password: the updated password
        """
        self.password = password

        db.session.commit()

    def to_dict(self):
        """A dictionary of all the values of this user object.

        :param self: This user object
        :return: A dictionary of the values of this user object
        """
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role,
            "active": self.active
        }


    def get_donation_code(self):
        """ Returns a code that will allow the user to donate if 
        the code is up-to-date with the database.

        :return: The current donation code
        """
        if donation_code is None or donation_code_is_stale:
            return create_donation_code()
        return donation_code


    def create_donation_code(self):
        """ Creates a randomly generated integer between 1-256 that 
        allows the user to donate if the correct code is held.
        
        :return: A randomly generated date hash
        """
        self.donation_code = hashlib.sha1(str(datetime.now())).hexdigest()
        return self.donation_code


    def validate_donation_code(self, code):
        """ Check if the given code has not matches the current one from the database

        :return: A new code if the given code is the most recent, None otherwise
        """
        if self.donation_code == code:
            create_donation_code()
            return self.donation_code
        else:
            False


    def has_suffcient_funds(self, amount):
        """Queries balance to check if user has sufficient funds to spend the given amount

        :param: Amount the user wants to check if they can spend
        """
        return amount <= self.balacnce


    @classmethod
    def from_dict(cls, data):
        """A dictionary of all the values of this user object.??

        :param data: The dictionary containing the users data
        :return: An object of this dictionaries data
        """
        # Ensure email address is case-insensitive
        email = data.get("email")
        if email is not None:
            data.update({"email": email.lower()})

        return cls(**data)


class InvalidUserInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
