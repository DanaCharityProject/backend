import json
from connexion import NoContent
from geopy.geocoders import Nominatim

from .auth import auth, current_user, current_role
from .models.user import User, InvalidUserInfo, USER_ROLE_ADMIN, USER_ROLE_USER
from .models.community_resource import CommunityResource, NoExistingCommunityResource, InvalidCommunityResourceInfo
from .models.community import Community
from .validators import is_valid_password, is_valid_email, is_valid_phone_number, is_valid_community_resource_name
from sqlalchemy import func

import sys

@auth.login_required
def get_user():
    return current_user().to_dict()


@auth.login_required
def put_user(body):
    user = current_user()

    try:
        user.edit_user(body["username"])
    except InvalidUserInfo:
        return NoContent, 500
    return NoContent, 200


def post_user(body):
    user = User.add_user(User.from_dict(body))

    if user is None:
        return NoContent, 409

    return user.to_dict(), 201


@auth.login_required
def put_user_password(body):
    current_user().change_password(body["password"])
    return NoContent, 200


@auth.login_required
def get_user_token():
    return {"token": current_user().generate_auth_token().decode("ascii")}, 201


def get_communityresource_list(longitude, latitude, radius):
    return [{
        "community_resource_id": community_resource.community_resource_id,
        "name": community_resource.name,
        "address": community_resource.address,
        "location": json.loads(location)
    } for (community_resource, location) in CommunityResource.get_resources_by_radius(longitude=longitude, latitude=latitude, radius=radius)]

def get_communityresource_in_shape(polygon_string):
    return [{
        "community_resource_id": community_resource.community_resource_id,
        "name": community_resource.name,
        "address": community_resource.address,
        "location": json.loads(location)
    } for (community_resource, location) in CommunityResource.get_resources_in_shape(polygon_string)]

@auth.login_required
def post_communityresource(body):
    if current_role() != USER_ROLE_ADMIN:
        return NoContent, 403

    charity_number = int(body["charity_number"])
    name = body["name"]
    address = body["address"]
    contact_name = body["contact_name"]
    email = body["email"]
    phone_number = body["phone_number"]
    website = body["website"]
    image_uri = body["image_uri"]

    longitude, latitude = CommunityResource.coordinates_from_address(address)

    resource = CommunityResource(charity_number=charity_number, 
                                 name=name, y=latitude, x=longitude,
                                 contact_name=contact_name, email=email,
                                 phone_number=phone_number, address=address,
                                 website=website, image_uri=image_uri,
                                 verified=True) #edited just here for now)
    
    resource = CommunityResource.add_community_resource(resource)

    if resource is None:
        return NoContent, 409

    return NoContent, 201


def get_communityresource_detail(community_resource_id):
    try:
        community_resource = CommunityResource.get_community_resource_by_id(community_resource_id)
    except NoExistingCommunityResource:
        return NoContent, 404
    return community_resource, 200


@auth.login_required
def put_communityresource(community_resource_id, body):
    if current_role() != USER_ROLE_ADMIN:
        return NoContent, 403
    try:
        (longitude, latitude) = CommunityResource.coordinates_from_address(body["address"])

        CommunityResource.edit_community_resource(int(body["charity_number"]), body["name"], latitude, longitude, body["contact_name"], body["email"], body["phone_number"], body["address"], body["website"], body["image_uri"])
    except NoExistingCommunityResource:
        return NoContent, 404
    except InvalidCommunityResourceInfo:
        return NoContent, 400
    return NoContent, 200


def get_all_communities():
    return [{
        "id": community.id,
        "name": community.name,
        "boundaries": json.loads(boundaries)
    } for (community, boundaries) in Community.get_all_communities()]


def get_community_surrounding(coordinates):
    res = Community.get_community_surrounding([float(s) for s in coordinates.split(',')])
    if res is None:
        return NoContent, 200
    else:
        return {
            "id": res[0].id,
            "name": res[0].name,
            "boundaries": res[1]
        }, 200


def get_donation_version():
    pass


def post_donation(name):
    pass
# def get_resource_by_radius(coordinates, radius):
#     """
#     cooridinates: the current position of where the user is.
#     radius: the distance from which the user wants to see the resources around them.
#     """
    
