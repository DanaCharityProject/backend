from .. import db
from .user import User

from flask import g
from sqlalchemy.ext.declarative import declared_attr


class Role(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def user_id(self):
        return db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)

    @staticmethod
    def is_allowed(role, roles):
        return any(isinstance(role, x) for x in roles)


class AdminRole(Role):
    __tablename__ = "adminroles"


class UserRole(Role):
    __tablename__ = "userroles"


class CommunityResourceRole(Role):
    __tablename__ = "communityresourceroles"
