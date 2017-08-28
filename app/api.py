from flask import g
from connexion import NoContent
from geopy.geocoders import Nominatim

from .auth import auth
from .models.user import User, UserManager, NoExistingUser, InvalidUserInfo
from .models.community_resource import CommunityResource, CommunityResourceManager, NoExistingCommunityResource, InvalidCommunityResourceInfo
from .validators import is_valid_password, is_valid_email, is_valid_phone_number, is_valid_community_resource_name


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
                                 phone_number=phone_number, verified=True) #edited just here for now)
    resource = CommunityResource.add_community_resource(resource)

    if resource is None:
        return NoContent, 500

    return resource.to_dict(), 200


def put_community_resource_edit(body):

    geolocator = Nominatim() # will copy over from master branch
    try:
        _, (lat, lon) = geolocator.geocode(body["address"])
    except expression as identifier:
        return NoContent, 500

    try:
        CommunityResourceManager.edit_community_resource(int(body["number"]), body["name"], lat, lon, body["contact_name"], body["email"], body["phone_number"]) 
    except NoExistingCommunityResource:
        return NoContent, 500
    except InvalidCommunityResourceInfo:
        return NoContent, 500
    return NoContent, 200


def put_community_resource_edit_name(body):

    try:
        CommunityResourceManager.edit_community_resource_name(int(body["number"]), body["name"]) 
    except NoExistingCommunityResource:
        return NoContent, 500
    except InvalidCommunityResourceInfo:
        return NoContent, 500
    return NoContent, 200


def put_community_resource_edit_address(body):

    geolocator = Nominatim() # will copy over from master branch
    try:
        _, (lat, lon) = geolocator.geocode(body["address"])
    except expression as identifier:
        return NoContent, 500

    try:
        CommunityResourceManager.edit_community_resource_location(int(body["number"]), lat, lon) 
    except NoExistingCommunityResource:
        return NoContent, 500
    except InvalidCommunityResourceInfo:
        return NoContent, 500
    return NoContent, 200


def put_community_resource_edit_contact_name(body):

    try:
        CommunityResourceManager.edit_community_resource_contact_name(int(body["number"]), body["contact_name"]) 
    except NoExistingCommunityResource:
        return NoContent, 500
    except InvalidCommunityResourceInfo:
        return NoContent, 500
    return NoContent, 200


def put_community_resource_edit_email(body):

    try:
        CommunityResourceManager.edit_community_resource_email(int(body["number"]), body["email"]) 
    except NoExistingCommunityResource:
        return NoContent, 500
    except InvalidCommunityResourceInfo:
        return NoContent, 500
    return NoContent, 200


def put_community_resource_edit_phone_number(body):

    try:
        CommunityResourceManager.edit_community_resource_phone_number(int(body["number"]), body["phone_number"]) 
    except NoExistingCommunityResource:
        return NoContent, 500
    except InvalidCommunityResourceInfo:
        return NoContent, 500
    return NoContent, 200


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
