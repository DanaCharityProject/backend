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
        return {
            "id": self.id,
            "name": self.name,
            "boundaries": self.boundaries
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    @classmethod
    def get_all_communities (cls):
        return db.session.query(Community, func.ST_AsGeoJSON(Community.boundaries)).all()

    @classmethod
    def get_community_surrounding(cls, coordinates):
        return db.session.query(
                Community, func.ST_AsGeoJSON(Community.boundaries)
            ).filter(
                func.ST_Contains(Community.boundaries, Community._array_to_point(coordinates))
            ).first()

    @classmethod
    def add_comunity(cls, community):
        db.session.add(community)
        db.session.commit()

        return community

    @staticmethod
    def populate_db():
        """Populate database with default community data."""
        Community._parse_shapefile_and_populate_db("/db_info/communities/NEIGHBORHOODS_WGS84.shp")

    @staticmethod
    def _parse_shapefile_and_populate_db(file_path):
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
                    "name": shapeRecord.record[field_dict['AREA_NAME']],
                    "boundaries": WKTElement(str(pygeoif.MultiPolygon(pygeoif.as_shape(shapeRecord.shape.__geo_interface__))), 4326)
                    }))
    
    @staticmethod
    def _array_to_point(arr):
        return WKTElement("POINT({} {})".format(arr[0], arr[1]), 4326)

