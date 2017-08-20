from .validators import is_valid_email, is_valid_phone_number, is_valid_community_resource_name
from .models import CommunityResource
from .exception_models import InvalidCommunityResourceInfo, NoExistingCommunityResource


class CommunityResourceManager():

    @staticmethod
    def edit_community_resource(number, new_name, new_lat, new_lon, new_contact_name, new_email, new_phone_number):
        resource = CommunityResource.get_resource_by_number(number)

        try:
            if resource is None:
                raise NoExistingCommunityResource("Community Resource does not exist.")
            if not is_valid_email(new_email):
                raise InvalidCommunityResourceInfo("New email address for Community Resource is invalid.")
            if not is_valid_phone_number(new_phone_number):
                raise InvalidCommunityResourceInfo("New phone number for Community Resource is invalid.")
            if not is_valid_community_resource_name(new_name):
                raise InvalidCommunityResourceInfo("New resource center name cannot be empty")
            resource.name = new_name
            resource.lat = new_lat
            resource.lon = new_lon
            resource.contact_name = new_contact_name
            resource.email = new_email
            resource.phone_number = new_phone_number
        except NoExistingCommunityResource:
            raise
        except InvalidCommunityResourceInfo:
            raise


    @staticmethod
    def edit_community_resource_name(number, new_name):
        resource = CommunityResource.get_resource_by_number(number)

        try:
            if resource is None:
                raise NoExistingCommunityResource("Community Resource does not exist.")
            if not is_valid_community_resource_name(new_name):
                raise InvalidCommunityResourceInfo("New resource center name cannot be empty")
            resource.name = new_name
        except NoExistingCommunityResource:
            raise
        except InvalidCommunityResourceInfo:
            raise


    @staticmethod
    def edit_community_resource_location(number, new_lat, new_lon):
        resource = CommunityResource.get_resource_by_number(number)

        try:
            if resource is None:
                raise NoExistingCommunityResource("Community Resource does not exist.")
            resource.lat = new_lat
            resource.lon = new_lon
        except NoExistingCommunityResource:
            raise
        except InvalidCommunityResourceInfo:
            raise


    @staticmethod
    def edit_community_resource_contact_name(number, new_contact_name):
        resource = CommunityResource.get_resource_by_number(number)

        try:
            if resource is None:
                raise NoExistingCommunityResource("Community Resource does not exist.")
            resource.contact_name = new_contact_name
        except NoExistingCommunityResource:
            raise
        except InvalidCommunityResourceInfo:
            raise

    @staticmethod
    def edit_community_resource_email(number, new_email):
        resource = CommunityResource.get_resource_by_number(number)

        try:
            if resource is None:
                raise NoExistingCommunityResource("Community Resource does not exist.")
            if not is_valid_email(new_email):
                raise InvalidCommunityResourceInfo("New email address for Community Resource is invalid.")
            resource.email = new_email
        except NoExistingCommunityResource:
            raise
        except InvalidCommunityResourceInfo:
            raise


    @staticmethod
    def edit_community_resource_phone_number(number, new_phone_number):
        resource = CommunityResource.get_resource_by_number(number)

        try:
            if resource is None:
                raise NoExistingCommunityResource("Community Resource does not exist.")
            if not is_valid_phone_number(new_phone_number):
                raise InvalidCommunityResourceInfo("New phone number for Community Resource is invalid.")
            resource.phone_number = new_phone_number
        except NoExistingCommunityResource:
            raise
        except InvalidCommunityResourceInfo:
            raise

