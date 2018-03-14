from .. import db
from ..validators import is_valid_username, is_valid_email, is_valid_phone_number, is_valid_community_resource_name
from geopy.distance import vincenty


class CommunityResource(db.Model):
    __tablename__ = "community resources"

    id = db.Column(db.Integer, primary_key=True)
    charity_number = db.Column(db.Integer, unique=True,
                       nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    y = db.Column(db.Float, nullable=False)
    x = db.Column(db.Float, nullable=False)
    contact_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)
    address = db.Column(db.String(64), nullable=False)
    website = db.Column(db.String(64), nullable=True)
    image_uri = db.Column(db.String(64), nullable=True)
    verified = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def location(self):
        return self.y, self.x

    def to_dict(self):
        return {
            "id": self.id,
            "charity_number": self.charity_number,
            "name": self.name,
            "y": self.y,
            "x": self.x,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
            "website": self.website,
            "image_uri": self.image_uri,
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

    # Returns a list of resources within a given radius of latitude, longitude
    @staticmethod
    def get_resources_by_radius(longitude, latitude, radius):
        res = CommunityResource.query.all()

        for c in res:
            if vincenty((c.x, c.y), (longitude, latitude)).kilometers > radius:
                res.remove(c)

        return res


class CommunityResourceManager():

    # TODO: check if address, website and image_uri are valid
    @staticmethod
    def edit_community_resource(charity_number, new_name, new_y, new_x, new_contact_name, new_email, new_phone_number, new_address, new_website, new_image_uri):
        resource = CommunityResource.get_resource_by_charity_number(charity_number)

        if resource is None:
            raise NoExistingCommunityResource("Community Resource does not exist.")

        if not is_valid_email(new_email):
            raise InvalidCommunityResourceInfo("New email address for Community Resource is invalid.")
        if not is_valid_phone_number(new_phone_number):
            raise InvalidCommunityResourceInfo("New phone number for Community Resource is invalid.")
        if not is_valid_community_resource_name(new_name):
            raise InvalidCommunityResourceInfo("New resource center name cannot be empty")

        resource.name = new_name
        resource.y = new_y
        resource.x = new_x
        resource.contact_name = new_contact_name
        resource.email = new_email
        resource.phone_number = new_phone_number
        resource.address = new_address
        resource.website = new_website
        resource.image_uri = new_image_uri

        #session.query(Stuff).update({Stuff.foo: Stuff.foo + 1})
        #session.commit()

        #db.session.add(resource)
        #db.session.update(resource)
        db.session.commit()  ##TODO: ask opinion
        #return resource


class NoExistingCommunityResource(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidCommunityResourceInfo(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


