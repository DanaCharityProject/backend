"""
Community Resource
====================================
The Community Resource module
"""
import os
import shapefile
import pygeoif

from .. import db
from ..validators import is_valid_username, is_valid_email, is_valid_phone_number, is_valid_community_resource_name
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from geoalchemy2 import WKTElement
from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Integer, Boolean, Float, func, select

class CommunityResource(db.Model):
    __tablename__ = "community_resources"

    community_resource_id = Column(Integer, primary_key=True)
    charity_number = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(64), nullable=False)
    coordinates = Column(Geometry('POINT', srid=4326), nullable=False)
    contact_name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    phone_number = Column(String(32), nullable=False)
    address = Column(String(64), nullable=False)
    website = Column(String(64), nullable=True)
    image_uri = Column(String(64), nullable=True)
    verified = Column(Boolean, default=False, nullable=False)

    @property
    def location(self):
        return self.coordinates

    def to_dict(self):
        """Return a dictionary representation of this CommunityResource object."""
        return {
            "id": self.community_resource_id,
            "charity_number": self.charity_number,
            "name": self.name,
            "coordinates": self.coordinates,
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
        """Create a CommunityResource object from a dict."""
        obj = cls(**data)

        if obj.coordinates is None:
            obj.coordinates = cls.coordinates_from_address(obj.address)

        return obj

    @classmethod
    def get_community_resource_by_id(cls, community_resource_id):
        """Return a GeoJSON representation of the CommunityResource with the given id."""
        community_resource = cls.query.filter_by(community_resource_id=community_resource_id).first()

        if community_resource is None:
            raise NoExistingCommunityResource("Community Resource does not exist.")

        coordinate_json = db.session.query(func.ST_AsGeoJSON(CommunityResource.coordinates)).filter_by(community_resource_id=community_resource_id).first()
        community_resource_geo_json = community_resource.to_dict()
        community_resource_geo_json['coordinates'] = coordinate_json

        return community_resource_geo_json

    @classmethod
    def get_community_resource_by_charity_number(cls, charity_number):
        """Return the CommunityResource with the given charity number."""
        return cls.query.filter_by(charity_number=charity_number).first()

    @classmethod
    def add_community_resource(cls, resource):
        """Add a given CommunityResource to the database. If there is a conflict,
        the existing object in the database is overwritten.
        """
        existing_resource = cls.query.filter_by(community_resource_id=resource.community_resource_id).first()

        if existing_resource is None:
            db.session.add(resource)
        else:
            existing_resource = resource

        db.session.commit()
        return resource

    # Returns a list of resources within a given radius of latitude, longitude
    @classmethod
    def get_resources_by_radius(cls, longitude, latitude, radius):
        """Given coordinates and a radius, return a list of CommunityResources within the
        given radius around the given coordinates in GeoJSON format.
        """
        return db.session.query(
                CommunityResource, func.ST_AsGeoJSON(CommunityResource.coordinates)
            ).filter(
                func.ST_DWITHIN(CommunityResource.coordinates, CommunityResource.long_lat_to_point(longitude, latitude), radius)
            ).all()
    
    @classmethod
    def get_resources_in_shape(cls, polygon_string):
        """Given a polygon, return a list of CommunityResources within the given polygon
        in GeoJSON format.
        """
        polygon = WKTElement(polygon_string, 4326)
        return db.session.query(
                CommunityResource, func.ST_AsGeoJSON(CommunityResource.coordinates)
            ).filter(
                func.ST_Contains(polygon, CommunityResource.coordinates)
            ).all()

    @staticmethod
    def coordinates_from_address(address):
        """Return the given address' coordinates."""
        geolocator = Nominatim()
        location = geolocator.geocode(address)

        return CommunityResource.long_lat_to_point(location.longitude, location.latitude)

    @classmethod
    def edit_community_resource(cls, community_resource_id, new_name, new_lat, new_long, new_contact_name, new_email, new_phone_number, new_address, new_website, new_image_uri):
        """Update and return the existing CommunityResource with the given id."""
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
        resource.coordinates = CommunityResource.long_lat_to_point(new_long, new_lat)
        resource.contact_name = new_contact_name
        resource.email = new_email
        resource.phone_number = new_phone_number
        resource.address = new_address
        resource.website = new_website
        resource.image_uri = new_image_uri

        db.session.commit()

        return resource

    @staticmethod
    def long_lat_to_point(longitude, latitude):
        """Return a WKTElement of the point with the given coordinates."""
        pointString = "POINT({} {})".format(longitude, latitude)
        return WKTElement(pointString, 4326)
    
    @staticmethod
    def populate_db():
        """Populate database with default data.
        """
        CommunityResource._parse_shapefile_and_populate_db("/db_info/shelters/shelters_wgs84.shp")
        CommunityResource._parse_shapefile_and_populate_db("/db_info/dropins/TDIN_wgs84.shp")

    @staticmethod
    def _parse_shapefile_and_populate_db(file_path):
        """Populate database with data from the shapefile with the given path."""
        if not os.path.exists(file_path):
            print(file_path + " does not exist")
        else:
            sf = shapefile.Reader(file_path)

            # Create a dict of {<field>: <index>}
            field_dict = {}
            for field in sf.fields:
                field_dict[field[0]] = sf.fields.index(field) - 1

            for shapeRecord in sf.shapeRecords():
                reversed = (shapeRecord.shape.__geo_interface__['coordinates'][1], shapeRecord.shape.__geo_interface__['coordinates'][0])
                coordinates = pygeoif.Point(pygeoif.geometry.as_shape({'type':'Point', 'coordinates': reversed}))
                CommunityResource.add_community_resource(CommunityResource.from_dict({
                    "community_resource_id": shapeRecord.record[field_dict['OBJECTID']],
                    "charity_number": shapeRecord.record[field_dict['OBJECTID']],
                    "name": shapeRecord.record[field_dict['NAME']],
                    "coordinates": WKTElement(str(pygeoif.Point(pygeoif.as_shape(coordinates))), 4326),
                    "contact_name":"",
                    "email":"",
                    "phone_number":"",
                    "address":"",
                    "website":"",
                    "image_uri":"",
                    "verified": True
                    }))


class NoExistingCommunityResource(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidCommunityResourceInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
