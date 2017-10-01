from .. import db
from ..validators import is_valid_username, is_valid_email, is_valid_phone_number, is_valid_community_resource_name


class CommunityResource(db.Model):
    __tablename__ = "community resources"

    id = db.Column(db.Integer, primary_key=True)
    charity_number = db.Column(db.Integer, unique=True,
                       nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    contact_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)

    @property
    def location(self):
        return self.lat, self.lon

    def to_dict(self):
        return {
            "id": self.id,
            "charity_number": self.charity_number,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "verified": self.verified
        }

    @staticmethod
    def get_resource_by_charity_number(charity_number):
        return CommunityResource.query.filter_by(charity_number=charity_number).first()

    @staticmethod
    def add_community_resource(resource):
        if CommunityResource.get_resource_by_charity_number(resource.charity_number) is not None:
            return None

        db.session.add(resource)
        db.session.commit()
        return resource


class CommunityResourceManager():

    @staticmethod
    def edit_community_resource(charity_number, new_name, new_lat, new_lon, new_contact_name, new_email, new_phone_number):
        resource = CommunityResource.get_resource_by_charity_number(charity_number)

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


class NoExistingCommunityResource(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidCommunityResourceInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


