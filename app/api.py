from flask import g
from connexion import NoContent
from geopy.geocoders import Nominatim

from .auth import auth
from .user_model import User
from .community_resource_model import CommunityResource
from .user_manager_model import UserManager
from .exception_models import NoExistingUser, InvalidUserInfo
from .validators import is_valid_password, is_valid_email


@auth.login_required
def get_greeting():

    return {
        "greeting": "Hello {}.".format(g.current_user.username)
    }


@auth.login_required
def get_user():
    return g.current_user.to_dict()


@auth.login_required
def get_user_token():
    return {"token": g.current_user.generate_auth_token().decode("ascii")}, 201


#   ---------


@auth.login_required
def post_greeting(body):

    return {
        "greeting": "Hello {}.".format(body["name"])
    }


def post_user(body):
    user = User(username=body["username"])
    user.password = body["password"]
    user = User.add_user(user)

    if user is None:
        return NoContent, 409

    return user.to_dict(), 201


# todo: make decorators for validation checks
# todo: fix imminent mistakes in api.yml file
def post_communityresource_register(body):
    number = int(body["number"])
    name = body["name"]
    address = body["address"]
    contact_name = body["contact_name"]
    email = body["email"]
    phone_number = body["phone_number"]

    geolocator = Nominatim()
    try:
        _, (lat, lon) = geolocator.geocode(address)
    except expression as identifier:
        return NoContent, 500

    resource = CommunityResource(number=number, name=name, lat=lat, lon=lon,
                                 contact_name=contact_name, email=email, 
                                 phone_number=phone_number)
    resource = CommunityResource.add_community_resource(resource)
    
    if resource is None:
        return NoContent, 500

    return resource.to_dict(), 200


#   ---------


@auth.login_required
def put_user_password(body):
    g.current_user.password = body["password"]

    return NoContent, 200


@auth.login_required
def put_user_info(body):
    user = g.current_user
    try:
        UserManager.edit_user(user.to_dict()["id"], body["username"])
    except NoExistingUser:
        return NoContent, 500
    except InvalidUserInfo:
        return NoContent, 500
    return NoContent, 200
