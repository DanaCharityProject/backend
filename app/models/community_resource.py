from .. import db
from ..validators import is_valid_username, is_valid_email, is_valid_phone_number, is_valid_community_resource_name
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from geoalchemy2.elements import WKTElement

class CommunityResource(db.Model):
    __tablename__ = "community_resources"

    community_resource_id = db.Column(db.Integer, primary_key=True)
    charity_number = db.Column(db.Integer, unique=True, nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    contact_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)
    address = db.Column(db.String(64), nullable=False)
    website = db.Column(db.String(64), nullable=True)
    image_uri = db.Column(db.String(64), nullable=True)
    verified = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def location(self):
        return self.y, self.x

    def to_dict(self):
        return {
            "id": self.community_resource_id,
            "charity_number": self.charity_number,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
            "website": self.website,
            "image_uri": self.image_uri,
            "verified": self.verified
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(**data)

        if obj.longitude is None or obj.latitude is None:
            obj.longitude, obj.latitude = cls.coordinates_from_address(obj.address)

        return obj

    @classmethod
    def get_community_resource_by_id(cls, communit_resource_id):
        return cls.query.get(communit_resource_id=communit_resource_id)

    @classmethod
    def get_community_resource_by_charity_number(charity_number):
        return cls.query.filter_by(charity_number=charity_number).first()

    @staticmethod
    def add_community_resource(resource):
        db.session.add(resource)
        db.session.commit()

        return resource

    # Returns a list of resources within a given radius of latitude, longitude
    @classmethod
    def get_resources_by_radius(cls, longitude, latitude, radius):
        all_community_resources = cls.query.all()

        for community_resource in all_community_resources:
            if vincenty((community_resource.longitude, community_resource.latitude), (longitude, latitude)).kilometers > radius:
                all_community_resources.remove(community_resource)

        return all_community_resources

    @staticmethod
    def coordinates_from_address(address):
        geolocator = Nominatim()
        location = geolocator.geocode(address)

        return (location.longitude, location.latitude)


    @classmethod
    def edit_community_resource(cls, community_resource_id, new_name, new_y, new_x, new_contact_name, new_email, new_phone_number, new_address, new_website, new_image_uri):
        resource = cls.get_resource_by_id(community_resource_id)

        if resource is None:
            raise NoExistingCommunityResource(
                "Community Resource does not exist.")

        if not is_valid_email(new_email):
            raise InvalidCommunityResourceInfo(
                "New email address for Community Resource is invalid.")
        if not is_valid_phone_number(new_phone_number):
            raise InvalidCommunityResourceInfo(
                "New phone number for Community Resource is invalid.")
        if not is_valid_community_resource_name(new_name):
            raise InvalidCommunityResourceInfo(
                "New resource center name cannot be empty")

        resource.name = new_name
        resource.y = new_y
        resource.x = new_x
        resource.contact_name = new_contact_name
        resource.email = new_email
        resource.phone_number = new_phone_number
        resource.address = new_address
        resource.website = new_website
        resource.image_uri = new_image_uri

        db.session.commit()

        return resource

    @staticmethod
    def __long_lat_to_point__(longitutde, latitude):
        pointString = "POINT({} {})".format(longitutde, latitude)
        return WKTElement(pointString, 4326)


class NoExistingCommunityResource(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidCommunityResourceInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
