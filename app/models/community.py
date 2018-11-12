"""
Community
====================================
The Community module
"""
import os
import shapefile
import pygeoif

from .. import db
from geoalchemy2 import WKTElement
from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Integer, func

class Community(db.Model):
    __tablename__ = "community"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    boundaries = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=False)

    def to_dict(self):
        """Return a dictionary representation of this Community object."""
        return {
            "id": self.id,
            "name": self.name,
            "boundaries": self.boundaries
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Community object from a dict."""
        return cls(**data)

    @classmethod
    def get_all_communities (cls):
        """Query the database and return a list of all Communities with their id, 
        name and boundaries in GeoJSON format.
        """
        return db.session.query(Community, func.ST_AsGeoJSON(Community.boundaries)).all()

    @classmethod
    def get_community_surrounding(cls, longitude, latitude):
        """Get a Community with boundaries surrounding a given point specified
        by longitude and latitude.  Returns the Community id, name and boundaries.
        """
        return db.session.query(
                Community, func.ST_AsGeoJSON(Community.boundaries)
            ).filter(
                func.ST_Contains(
                    Community.boundaries, 
                    WKTElement("POINT({} {})".format(longitude, latitude), 4326))
            ).first()

    @classmethod
    def add_comunity(cls, community):
        """Add a given Community to the database.  If there is a conflict,
        the existing object in the database is overwritten.
        """
        existing_community = cls.query.filter_by(id=community.id).first()

        if existing_community is None:
            db.session.add(community)
        else:
            existing_community = community

        db.session.commit()
        return community

    @staticmethod
    def populate_db():
        """Populate database with default community data."""
        Community._parse_shapefile_and_populate_db("/db_info/communities/NEIGHBORHOODS_WGS84.shp")

    @staticmethod
    def _parse_shapefile_and_populate_db(file_path):
        """Given a path to a shapefile containing Community information, 
        parse the file and add each Community to the database.
        """
        if not os.path.exists(file_path):
            print(file_path + " does not exist")
        else:
            sf = shapefile.Reader(file_path)

            # Create a dict of {<field>: <index>}
            field_dict = {}
            for field in sf.fields:
                field_dict[field[0]] = sf.fields.index(field) - 1

            for shapeRecord in sf.shapeRecords():
                Community.add_comunity(Community.from_dict({
                    "id": shapeRecord.record[field_dict['AREA_S_CD']],
                    "name": ' '.join(shapeRecord.record[field_dict['AREA_NAME']].split(' ')[:-1]),
                    "boundaries": WKTElement(str(pygeoif.MultiPolygon(pygeoif.as_shape(Community._longlat_to_latlong(shapeRecord.shape.__geo_interface__)))), 4326)
                    }))
    
    @staticmethod
    def _longlat_to_latlong(geojson):
        """Given a GeoJSON in dict form, reverses the order of
        the coordinates.
        """
        coordinates = geojson['coordinates']
        new_coordinates = ()

        for polygon in coordinates:
            new_polygon = (())
            for point in polygon:
                new_point = (point[1], point[0])
                new_polygon += (new_point),
            
            new_coordinates += (new_polygon),

        return {
            'type': 'Polygon',
            'coordinates': new_coordinates
        }
