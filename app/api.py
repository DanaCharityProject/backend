import json

from flask import g
from connexion import NoContent
from geopy.geocoders import Nominatim

from .auth import auth
from .models.user import User, UserManager, NoExistingUser, InvalidUserInfo
from .models.community_resource import CommunityResource, CommunityResourceManager, NoExistingCommunityResource, InvalidCommunityResourceInfo
from .validators import is_valid_password, is_valid_email, is_valid_phone_number, is_valid_community_resource_name


@auth.login_required
def get_user():
    return g.current_user.to_dict()


@auth.login_required
def get_user_token():
    return {"token": g.current_user.generate_auth_token().decode("ascii")}, 201


def get_communityresource_info(body):
    try:
        com_resource = CommunityResource.get_resource_by_charity_number(charity_number=body["charity_number"])
    except NoExistingCommunityResource:
        return NoContent, 500

    com_resource_dict = com_resource.to_dict()
    return_dict = {
        "name": com_resource_dict["name"],
        "website": com_resource_dict["website"],
        "address": com_resource_dict["address"],
        "image_uri": com_resource_dict["image_uri"]
    }

    return json.dumps(return_dict, sort_keys=True), 200


#   ---------

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
    charity_number = int(body["charity_number"])
    name = body["name"]
    address = body["address"]
    contact_name = body["contact_name"]
    email = body["email"]
    phone_number = body["phone_number"]
    website = body["website"]
    image_uri = body["image_uri"]

    try:
        (lon, lat) = __get_coordinates_from_address(address)
    except expression as identifier:
        return NoContent, 500

    resource = CommunityResource(charity_number=charity_number, name=name, y=lat, x=lon,
                                 contact_name=contact_name, email=email,
                                 phone_number=phone_number, address=address,
                                 website=website, image_uri=image_uri,
                                 verified=True) #edited just here for now)
    resource = CommunityResource.add_community_resource(resource)

    if resource is None:
        return NoContent, 500

    return resource.to_dict(), 200


def put_community_resource_edit(body):

    #geolocator = Nominatim() # will copy over from master branch
    try:
        #_, (lat, lon) = geolocator.geocode(body["address"])
        (lon, lat) = __get_coordinates_from_address(body["address"])
    except expression as identifier:
        return NoContent, 500

    try:
        CommunityResourceManager.edit_community_resource(int(body["charity_number"]), body["name"], lat, lon, body["contact_name"], body["email"], body["phone_number"], body["address"], body["website"], body["image_uri"])
    except NoExistingCommunityResource:
        return NoContent, 500
    except InvalidCommunityResourceInfo:
        return NoContent, 500
    return NoContent, 200


@auth.login_required
def put_user_password(body):
    UserManager.change_password(g.current_user, body["password"])
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


def __get_coordinates_from_address(body_address):
    geolocator = Nominatim()
    location = geolocator.geocode(body_address)
    try:
        return (location.longitude, location.latitude)  #x, y
    except expression as identifier:
        return NoContent, 500